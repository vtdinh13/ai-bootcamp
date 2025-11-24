import pytest 

import wikiagent.main as main
from tests.judge_utils import evaluate_with_judge
from tests.utils import get_tool_calls

@pytest.mark.asyncio
async def test_eval_agent():
    user_input = "where do cabybara live?"

    result = await main.run_agent(user_input)

    print(result.output)
    
    criteria = ["agent followed directions", "answers are relevant"]

    tool_calls = get_tool_calls(result)

    judge_feedback = await evaluate_with_judge(
        criteria,
        result.output,
        tool_calls,
    )

    print(judge_feedback)

    for criterion in judge_feedback.criteria:
        assert criterion.passed, f"Criterion failed: {criterion.criterion_description}, {criterion.judgement}"
