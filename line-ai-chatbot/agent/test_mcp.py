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
    print(tools)
    agent = create_react_agent(model, tools)
    response = await agent.ainvoke({"messages": query})
    return response


def serialize_response(obj: Any) -> Any:
    """Helper function to make the response JSON serializable."""
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


def print_tool_calls(response):
    """Print tool calls from the response object."""
    for message in response["messages"]:
        if hasattr(message, "additional_kwargs") and message.additional_kwargs.get("tool_calls"):
            tool_calls = message.tool_calls
            print("\n------------Tool Calls------------")
            for tool_call in tool_calls:
                print(f"Tool Name: {tool_call['name']}")
                print(f"Tool ID: {tool_call['id']}")
                print("Arguments:", json.dumps(tool_call['args'], indent=2))
                print("------------------------")


def print_ai_messages(response):
    """Print all non-empty AI messages from the response."""
    for message in response["messages"]:
        if type(message).__name__ == "AIMessage" and message.content:
            print("\n------------AI Message------------")
            print(f"Content: {message.content}")
            print("--------------------------------")

def process_and_print_response(response):
        """Process and print the response from the agent."""
        #json_response = json.dumps(response, default=serialize_response, indent=2)
        #print("\n------------Json Response------------")
        #print(json_response)
        print_tool_calls(response)   
        print_ai_messages(response)


if __name__ == "__main__":
    
    response = asyncio.run(main(f"台北現在天氣如何"))
    process_and_print_response(response)
    
    # response = asyncio.run(main(f"3 + 5 x 12"))
    # process_and_print_response(response)
