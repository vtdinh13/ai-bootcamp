"""Shared judge/evaluation helpers for realtime and log-based tests."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from pydantic import BaseModel
from pydantic_ai import Agent

from .utils import ToolCall

judge_instructions = (
    "you are an expert judge evaluating the performance of an AI agent."
)


class JudgeCriterion(BaseModel):
    criterion_description: str
    passed: bool
    judgement: str


class JudgeFeedback(BaseModel):
    criteria: list[JudgeCriterion]
    feedback: str


def create_judge() -> Agent:
    """Instantiate the judge agent."""

    return Agent(
        name="judge",
        instructions=judge_instructions,
        model="openai:gpt-4o-mini",
        output_type=JudgeFeedback,
    )


async def evaluate_with_judge(
    criteria: Sequence[str],
    agent_output: str,
    tool_calls: Sequence[ToolCall],
    *,
    judge: Agent | None = None,
    output_transformer: Callable[[str], str] | None = None,
) -> JudgeFeedback:
    """Run the judge against a finished agent output + tool metadata."""

    judge = judge or create_judge()

    processed_output = (
        output_transformer(agent_output)
        if output_transformer is not None
        else agent_output
    )

    criteria_str = "\n".join(criteria)
    if tool_calls:
        tool_calls_str = "\n".join(
            f"{call.name}: {call.args}" for call in tool_calls
        )
    else:
        tool_calls_str = "No tool calls recorded."

    user_prompt = f"""
    Evaluate the agent's performance based on the following criteria:
    <CRITERIA>
    {criteria_str}
    </CRITERIA>

    The agent's final output was:
    <AGENT_OUTPUT>
    {processed_output}
    </AGENT_OUTPUT>

    Tool calls:
    <TOOL_CALLS>
    {tool_calls_str}
    </TOOL_CALLS>
    """.strip()

    eval_results = await judge.run(user_prompt=user_prompt)
    return eval_results.output
