import streamlit as st
import sys
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
from scripts import base_tools, prompts

# api_key = os.getenv("GROQ_API_KEY")
load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    #model="llama-3.3-70b-versatile",
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0.7
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    sys.stdout.reconfigure(encoding="utf-8")




async def get_tools():
    client = MultiServerMCPClient(
        {
            "airbnb": {
                "command": "npx",
                "args": [
                    "-y",
                    "@openbnb/mcp-server-airbnb",
                    "--ignore-robots-txt"
                ],
                "transport": "stdio"
            }
        }
    )
    mcp_tools = await client.get_tools()
    tools = mcp_tools + [base_tools.get_weather, base_tools.web_search]
    return tools

async def hotel_search(query):
    tools = await get_tools()
    agent = create_agent(model=llm, tools=tools, system_prompt=prompts.AIRBNB_PROMPT)

    result = await agent.ainvoke({"messages": [HumanMessage(query)]})

    output = result["messages"][-1].text
    return output

# Streamlit UI
st.title("Airbnb Hotel Search")

st.write(
    """
    Enter your query below to search for Airbnb hotels. You can ask questions like:
    - "Find hotels in Paris"
    - "What is the price for a hotel in NYC?"
    - "Find a 2-bedroom apartment in San Francisco."
    """
)

query = st.text_input("Enter your query:", "")

if query:
    if query.lower() not in ['q', 'exit', 'quit']:
        # Run the search asynchronously in the Streamlit front-end
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output = loop.run_until_complete(hotel_search(query))
        st.subheader("Search Results:")
        st.write(output)
    else:
        st.write("Exiting the search.")
else:
    st.write("Please enter a query to search.")