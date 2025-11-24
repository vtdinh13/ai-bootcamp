from tools import search, get_page
from pydantic_ai import Agent
from pydantic_ai.messages import FunctionToolCallEvent

class NamedCallback:

    def __init__(self, agent):
        self.agent_name = agent.name

    async def print_function_calls(self, ctx, event):
        # Detect nested streams
        if hasattr(event, "__aiter__"):
            async for sub in event:
                await self.print_function_calls(ctx, sub)
            return

        if isinstance(event, FunctionToolCallEvent):
            tool_name = event.part.tool_name
            args = event.part.args
            print(f"TOOL CALL ({self.agent_name}): {tool_name}({args})")

    async def __call__(self, ctx, event):
        return await self.print_function_calls(ctx, event)


agent_instructions = """

You are a research assistant for Wikipedia topics.

Process:
1) Extract a list of DISTINCT, relevant search terms for the user query using the search() tool. 
2) For EACH term in that list, call the tool get_page() to fetch content for each distinct term. Make at least 3 calls and no more than 7 calls.
3) Do not synthesize an answer until you have called `get_page` on at least 3 distinct terms.
4) After collecting pages, synthesize a concise, accurate answer with references for each section.

Rules:
- You MUST call `get_page` once per term.
- Keep the list short (3–7 terms) and relevant.

You have access to the following tools:
- search - Use this tool to search the Wikipedia API for pertinent topics relating to the full search term provided by the user.
- get_page - Use this tool to search Wikipedia for information regarding pertinent topics provided by the Wikipedia API.

""".strip()

tool_methods = [
    search, get_page
]

def create_agent():
    agent = Agent(
        name='research assistant',
        tools=tool_methods,
        instructions=agent_instructions,
        model='openai:gpt-4o-mini')
    return agent

