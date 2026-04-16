import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(root)

sys.path.append(root)

from dotenv import load_dotenv

load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from scripts import base_tools, prompts, utils
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
import asyncio

load_dotenv()


# # Initialize Groq LLM
# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0.7,  #########  groq doesnt work with google mcp
# )
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
checkpointer = InMemorySaver()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # it was suggested
    sys.stdout.reconfigure(encoding="utf-8")


async def get_tools():
    client = MultiServerMCPClient(
        utils.load_mcp_config(
            "yahoo-finance", "google-sheets", "gmail", "google-calendar"
        )
    )
    mcp_tools = await client.get_tools()
    tools = mcp_tools + [base_tools.get_weather, base_tools.web_search]

    # Filter tools that work with Gemini
    problematic_tools = [
        "update_cells",
        "delete_email",
        "modify_email",
        "batch_modify_emails",
        "batch_delete_emails",
    ]

    safe_tool = [tool for tool in tools if tool.name not in problematic_tools]
    # print(f"Number of tools {len(safe_tool)}")
    # print(f"Loaded tools:\n{[tool.name for tool in safe_tool]}")
    return safe_tool


async def gmail_agent(query,thread_id='123'):
    tools = await get_tools()
    agent = create_agent(model=llm, tools=tools, system_prompt=prompts.agent_prompt(),
                         checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": thread_id}}

    result = await agent.ainvoke({"messages": [HumanMessage(query)]}, config=config)

    output = result["messages"][-1].text
    print("\n" + "==" * 60)
    print(output)

checkpointer = InMemorySaver()
async def ask():
    while True:
        print("Gmail_Agent")
        query = input("Enter your query...(press q  to exit) \n Query: ").strip()

        if query.lower() in ["q", "exit", "quit"]:
            print("exiting...")
            break
        await gmail_agent(query)


if __name__ == "__main__":

    asyncio.run(ask())
