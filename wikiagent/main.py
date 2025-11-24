import wikiagent
# import asyncio

agent = wikiagent.create_agent()
agent_callback = wikiagent.NamedCallback(agent)

async def run_agent(user_prompt: str):

    results = await agent.run(
        user_prompt=user_prompt,
        event_stream_handler=agent_callback
    )

    return results

# def run_agent_sync(user_prompt:str):
#     return asyncio.run(run_agent(user_prompt))

# result = asyncio.run(run_agent('where do cabybaras live?'))
# print(result.output)

# def main():
    
# if __name__ == '__main__':
#     main()