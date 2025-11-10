import main
from agents import Agent
from tests.utils import get_tool_calls


def test_search():
    user_prompt = 'where do cabybara live?'
    result = main.run_agent_sync(user_prompt)
    print(result.output)

    tool_calls = get_tool_calls(result)
    assert len(result.output) > 0, f"Expected success return of a GET request"


def test_3_wiki_searches():
    user_prompt = 'where do cabybara live?'
    result = main.run_agent_sync(user_prompt)
    tool_calls = get_tool_calls(result)

    get_page_count = sum(t.name == 'get_page' for t in tool_calls)

    assert get_page_count >=3, f"Expected at least 3 tool calls, got {get_page_count}"
