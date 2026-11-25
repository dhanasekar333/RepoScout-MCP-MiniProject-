import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from reposcout.config import CONFIG, SYSTEM_PROMPT


@asynccontextmanager
async def lifespan(app):
    # Open the MCP connections ONCE when the server starts, close at shutdown
    async with MCPAdapter(CONFIG) as adapter:
        tools = await adapter.list_tools()
        print("Tools loaded:", [t.name for t in tools])

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        app.state.agent = create_agent(
            model,
            tools,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=InMemorySaver(),  # remembers each thread_id
        )
        yield


app = FastAPI(lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    thread_id: str


@app.post("/ask")
async def ask(body: AskRequest, x_api_key: str = Header(None)):
    # Simple auth: compare with the key stored in .env
    if x_api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(status_code=401, detail="Bad API key")

    result = await app.state.agent.ainvoke(
        {"messages": [{"role": "user", "content": body.question}]},
        config={"configurable": {"thread_id": body.thread_id}},
    )
        # Print every tool call and tool result to the terminal
    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            print("TOOL CALL:", message.tool_calls)
        if message.type == "tool":
            print("TOOL RESULT:", str(message.content)[:500])
    return {"answer": result["messages"][-1].content}