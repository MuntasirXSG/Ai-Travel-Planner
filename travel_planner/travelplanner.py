import sys 
import os 

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print (root)

sys.path.append(root)

from dotenv import load_dotenv

load_dotenv()

from scripts import utils 
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from scripts import base_tools, prompts
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
import asyncio

load_dotenv()


# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7
)

checkpointer = InMemorySaver()
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) #it was suggested 
    sys.stdout.reconfigure(encoding="utf-8")

async def get_tools():
   client = MultiServerMCPClient( utils.load_mcp_config('airbnb', 'google-calendar')
   
)
   mcp_tools = await client.get_tools()
   tools = mcp_tools + [base_tools.get_weather, base_tools.web_search]
   print(f"Number of tools {len(tools)}")
   print(f"Loaded tools:\n{[tool.name for tool in tools]}")
   return tools

prompt=''''''

async def planner(query, thread_id="user"):
    tools = await get_tools()
    agent = create_agent(model=llm, tools=tools, system_prompt=prompt, checkpointer=checkpointer)
    config = {'configurable':{'thread_id' : thread_id}}
    output= len(tools)
    
    result = await agent.ainvoke({"messages":[HumanMessage(query)]}, config=config)

    output = result["messages"][-1].text
    print('\n' +"=="*60)
    print(output)
  
async def search():
    while True:
        print("Travel Planner Agent")    
        query = input("Enter your query...(press q  to exit) \n Query: ").strip()

        if query.lower() in ['q','exit','quit']:
            print("exiting...")
            break
        await planner(query)  
 


if __name__=="__main__":
   
    asyncio.run(search())    