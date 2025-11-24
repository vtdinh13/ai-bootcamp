"""Evaluate stored agent logs with the same judge used in realtime tests."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path
from typing import Iterable

from tests.judge_utils import JudgeFeedback, evaluate_with_judge
from tests.utils import ToolCall


DEFAULT_CRITERIA = [
    "agent followed directions",
    "answers are relevant",
]

CSV_HEADERS = [
    "log_path",
    "agent_output",
    "all_criteria_passed",
    "feedback_summary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the judge against completed agent runs that were written to log "
            "files."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["logs"],
        help="Log files or directories to evaluate (defaults to ./logs)",
    )
    parser.add_argument(
        "--criteria",
        action="append",
        default=[],
        help="Additional evaluation criteria (can be passed multiple times)",
    )
    parser.add_argument(
        "--csv-out",
        default="log_evaluations.csv",
        help="Where to write the CSV summary of agent responses",
    )
    return parser.parse_args()


def discover_logs(targets: Iterable[str]) -> list[Path]:
    """Expand directories into log file paths."""

    paths: list[Path] = []
    for target in targets:
        path = Path(target)
        if path.is_file():
            paths.append(path)
        elif path.is_dir():
            paths.extend(sorted(path.glob("*.json")))
        else:
            raise FileNotFoundError(f"Path does not exist: {path}")
    return paths


def extract_output(log_data: dict) -> str:
    """Return the agent output stored in the log."""

    if output := log_data.get("output"):
        return output

    # Fallback: grab the final text part in the message list.
    messages = log_data.get("messages", [])
    for message in reversed(messages):
        for part in reversed(message.get("parts", [])):
            if part.get("part_kind") == "text" and part.get("content"):
                return part["content"]
    raise ValueError("No agent output found in log data")


def extract_tool_calls(log_data: dict) -> list[ToolCall]:
    calls: list[ToolCall] = []
    for message in log_data.get("messages", []):
        for part in message.get("parts", []):
            if part.get("part_kind") != "tool-call":
                continue
            args = part.get("args")
            if isinstance(args, str):
                try:
                    parsed_args = json.loads(args)
                except json.JSONDecodeError:
                    parsed_args = {"raw": args}
            elif isinstance(args, dict):
                parsed_args = args
            else:
                parsed_args = {"raw": args}
            calls.append(
                ToolCall(name=part.get("tool_name", "unknown"), args=parsed_args)
            )
    return calls


async def evaluate_log(path: Path, criteria: list[str]) -> tuple[Path, str, JudgeFeedback]:
    data = json.loads(path.read_text())
    output = extract_output(data)
    tool_calls = extract_tool_calls(data)

    feedback = await evaluate_with_judge(criteria, output, tool_calls)

    print(f"=== {path} ===")
    for criterion in feedback.criteria:
        status = "PASS" if criterion.passed else "FAIL"
        print(f"- {status} :: {criterion.criterion_description}")
        print(f"  {criterion.judgement}")
    print(f"Feedback summary: {feedback.feedback}\n")

    return path, output, feedback


def append_csv_rows(csv_path: Path, rows: list[dict[str, object]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


async def main() -> None:
    args = parse_args()
    criteria = DEFAULT_CRITERIA + args.criteria
    log_paths = discover_logs(args.paths)

    if not log_paths:
        raise SystemExit("No log files found to evaluate.")

    rows: list[dict[str, object]] = []
    for path in log_paths:
        log_path, agent_output, feedback = await evaluate_log(path, criteria)
        rows.append(
            {
                "log_path": str(log_path),
                "agent_output": agent_output,
                "all_criteria_passed": all(
                    criterion.passed for criterion in feedback.criteria
                ),
                "feedback_summary": feedback.feedback,
            }
        )

    append_csv_rows(Path(args.csv_out), rows)


if __name__ == "__main__":
    asyncio.run(main())
