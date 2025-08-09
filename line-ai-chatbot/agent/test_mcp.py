from typing import Any
import asyncio
import json

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()


# Initialize model
model = init_chat_model(model="bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0")


async def main(query: str):
    """Main function to process queries using the MCP client."""
    client = MultiServerMCPClient({
        "waather": {
            "url": "http://127.0.0.1:9000/mcp",  # Replace with the remote server's URL
            "transport": "streamable_http"
        },
        "Math": {
            "url": "http://127.0.0.1:7000/mcp",  # Replace with the remote server's URL
            "transport": "streamable_http"
        }
    })
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    response = await agent.ainvoke({"messages": query})
    return response



if __name__ == "__main__":
    
    response = asyncio.run(main(f"台北現在天氣如何"))
    print(response['messages'][-1].content)
    
    # response = asyncio.run(main(f"3 + 5 x 12"))
    # process_and_print_response(response)
