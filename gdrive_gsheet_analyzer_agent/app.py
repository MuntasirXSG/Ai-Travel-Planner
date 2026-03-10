import streamlit as st
import sys
import os
import asyncio

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

from scripts import base_tools, prompts, utils

load_dotenv()

# ---------- LLM ----------
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
)

checkpointer = InMemorySaver()

# Windows async fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ---------- Load Tools ----------
async def get_tools():

    client = MultiServerMCPClient(
        utils.load_mcp_config("yahoo-finance", "google-sheets")
    )

    mcp_tools = await client.get_tools()

    tools = mcp_tools + [
        base_tools.get_weather,
        base_tools.web_search,
    ]

    problematic_tools = [
        "update_cells",
    ]

    safe_tools = [tool for tool in tools if tool.name not in problematic_tools]

    return safe_tools


# ---------- Agent ----------
async def run_agent(query, thread_id="user"):

    tools = await get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=prompts.GOOGLE_SHEETS_PROMPT,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": thread_id}}

    result = await agent.ainvoke(
        {"messages": [HumanMessage(query)]},
        config=config,
    )

    return result["messages"][-1].text


# ---------- Streamlit UI ----------
st.set_page_config(page_title="AI Agent", page_icon="🤖")

st.title("🤖 MCP AI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Ask something...")

if user_input:

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = asyncio.run(run_agent(user_input))

            st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
