import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

load_dotenv()
from reposcout.config import CONFIG, SYSTEM_PROMPT

# Test Script. main script in app.py
async def main():
    async with MCPAdapter(CONFIG) as adapter:
        tools = await adapter.list_tools()
        print([t.name for t in tools])   # check the names first

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)

        response = await agent.ainvoke(
            {"messages": [{"role": "user",
                           "content": "How is routing structured in the fastapi/fastapi repo?"}]}
        )
        print(response["messages"][-1].content)

asyncio.run(main())