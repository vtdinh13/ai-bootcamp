import pytest 
from pydantic_ai import Agent, AgentRunResult
from pydantic import BaseModel


from tests.utils import get_tool_calls
import main

judge_instructions = """
you are an expert judge evaluating the performance of an AI agent.
""".strip()


class JudgeCriterion(BaseModel):
    criterion_description: str
    passed: bool
    judgement: str


class JudgeFeedback(BaseModel):
    criteria: list[JudgeCriterion]
    feedback: str


def create_judge():
    judge = Agent(
        name="judge",
        instructions=judge_instructions,
        model="openai:gpt-4o-mini",
        output_type=JudgeFeedback,
    )
    return judge
async def evaluate_agent_performance(
        criteria: list[str],
        result: AgentRunResult,
        output_transformer: callable = None
) -> JudgeFeedback:
    judge = create_judge()

    tool_calls = get_tool_calls(result)

    output = result.output
    if output_transformer is not None:
        output = output_transformer(output)

    criteria_str = "\n".join(criteria)
    tool_calls_str = "\n".join(str(c) for c in tool_calls)

    user_prompt = f"""
    Evaluate the agent's performance based on the following criteria:
    <CRITERIA>
    {criteria_str}
    </CRITERIA>

    The agent's final output was:
    <AGENT_OUTPUT>
    {output}
    </AGENT_OUTPUT>

    Tool calls:
    <TOOL_CALLS>
    {tool_calls_str}
    </TOOL_CALLS>
    """

    print("Judge evaluating with prompt:")
    print("-----")
    print(user_prompt)
    print("-----")

    eval_results = await judge.run(
        user_prompt=user_prompt
    )

    return eval_results.output

@pytest.mark.asyncio
async def test_eval_agent():
    user_prompt = "what is the best way to drink coffee?"

    result = await main.run_agent(user_prompt)

    print(result.output)
    
    criteria = [
        "sucessful return from Wikipedia API",
        "agent made at least 3 get_page tool calls",
    ]

    judge_feedback = await evaluate_agent_performance(
        criteria,
        result,
        output_transformer=lambda output: output
    )

    print(judge_feedback)

    for criterion in judge_feedback.criteria:
        assert criterion.passed, f"Criterion failed: {criterion.criterion_description}, {criterion.judgement}"