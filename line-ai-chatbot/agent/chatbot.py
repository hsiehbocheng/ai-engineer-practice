from typing import Annotated
import os
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "cathay-agent-club"
chat_model_name = 'bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0'

llm = init_chat_model(model=chat_model_name)

def call_llm(messages: str):
    response = llm.invoke(messages)
    
    return response.content

if __name__ == "__main__":
    print(call_llm("hi"))