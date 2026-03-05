import os
import json

from langchain.tools import tool
import ollama
import requests

# -------------------------
# MCP Config Loader
# -------------------------



# -------------------------
# Web Search Tool
# -------------------------

@tool
async def web_search(query: str):
    """
    Perform a live web search using Ollama Cloud Web Search API for real-time information and news.


    """

    response = ollama.web_search(query=query, max_results=2)
    response = response.results

    return response


# -------------------------
# Weather Tool
# -------------------------
# @tool

# def get_weather(location: str):
#     """Get current weather for a location using WeatherAPI.com.
    
#     Use for queries about weather, temperature, or conditions in any city.
#     Examples: "weather in Paris", "temperature in Tokyo", "is it raining in London"
    
#     Args:
#         location: City name (e.g., "New York", "London", "Tokyo")
        
#     Returns:
#         Current weather information including temperature and conditions.
#     """

#     url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

#     response = requests.get(url=url, timeout=10)
#     response.raise_for_status()

#     data = response.json()

   # return data

'''🚨 What Was The Real Problem?

Your original tool returned this:

return data

That means it returned a Python dict.

But when using:

Groq

Tool calling

LangGraph / LangChain tool schema

Groq expects tool outputs to be serializable strings, not raw Python objects.

🧠 What Happened Internally

Here’s what the flow looks like:

Model decides to call tool:

airbnb_search(...)

Tool executes.

Tool returns a Python dict.

LangChain tries to send that back to Groq as part of conversation.

Groq expects tool responses to be:

{
  "role": "tool",
  "content": "STRING"
}

Instead it received structured JSON object.

💥 Groq rejected it with:

tool_use_failed
invalid_request_error
🎯 Why Returning String Fixed It

You changed:

return data

to:

return json.dumps(result)

Now:

✔ The tool output is a plain string
✔ It fits Groq’s expected schema
✔ It becomes valid "tool message content"
✔ No serialization conflict

So the LLM receives:

"{'city': 'Boston', 'temperature_c': 12, ...}"

instead of raw Python dict.'''

from langchain_core.tools import tool
import requests
import os
import json

@tool
def get_weather(location: str) -> str:
    """Get current weather for a city."""

    url = f"http://api.weatherapi.com/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    result = {
        "city": data["location"]["name"],
        "country": data["location"]["country"],
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"]
    }

    return json.dumps(result)