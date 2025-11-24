import wikiagent
import asyncio
from agent_logging import log_streamed_run, save_log


async def main():

    user_input = "where do cabybaras live?"

    agent = wikiagent.create_agent()
    agent_callback = wikiagent.NamedCallback(agent)

    previous_text = ""

    async with agent.run_stream(user_input, event_stream_handler=agent_callback) as result:
        async for item, last in result.stream_responses(debounce_by=0.01):
            for part in item.parts:
                if not hasattr(part, "tool_name"):
                    continue
                if part.tool_name != "final_result":
                    continue

                current_text = part.args
                delta = current_text[len(previous_text):]
                # print(delta, end="", flush=True)

                previous_text = current_text
        log_entry = await log_streamed_run(agent, result)
        save_log(log_entry)


    # results = await agent.run(
    #     user_prompt=user_prompt,
    #     event_stream_handler=agent_callback
    # )
    # return results



    
if __name__ == '__main__':
    asyncio.run(main())