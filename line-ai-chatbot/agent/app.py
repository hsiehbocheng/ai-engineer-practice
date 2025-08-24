from regex import R
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Body
from langchain_core.messages import ToolMessage, AIMessage

from chatbot.agent import create_graph, call_agent
from chatbot.agent import (
    structure_parking_info, 
    structure_toilet_info, 
    structure_agent_response,
    summarize_agent_response
)
from chatbot.agent import checkpointer

from chatbot.models import ParkingInfoList, ToiletInfoList, AgentStructureResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.agent = await create_graph(checkpointer)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health():
    return {"status": "200"}

@app.get("/chat")
async def chat(user_id: str, query: str):
    agent = getattr(app.state, "agent", None)
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    response = await call_agent(agent, user_id, query)
    response = response['messages'][-1].content
    
    return response

@app.post("/get_parking_info", response_model=ParkingInfoList)
async def get_parking_info(query: str = Body(...)):
    # (deprecated) should use get_agent_structure_response instead
    response = await structure_parking_info(query)
    
    return response

@app.post("/get_toilet_info", response_model=ToiletInfoList)
async def get_toilet_info(query: str = Body(...)):
    # (deprecated) should use get_agent_structure_response instead
    response = await structure_toilet_info(query)
    
    return response

@app.post("/get_agent_structure_response", response_model=AgentStructureResponse)
async def get_agent_structure_response(query: str = Body(...)):
    response = await structure_agent_response(query)
    
    return response

@app.post("/get_llm_summary", response_model=str)
async def get_llm_summary(query: str = Body(...)):
    response = await summarize_agent_response(query)
    
    return response.content


@app.get("/latest_tool_call")
async def get_latest_tool_call(user_id: str):
    agent = getattr(app.state, "agent", None)
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    config = {"configurable": {"thread_id": user_id}}
    snapshots = list(agent.get_state_history(config))
    
    for snapshot in snapshots:
        msgs = snapshot.values.get('messages', [])
        for msg in reversed(msgs):
            if isinstance(msg, AIMessage):
                tool_calls = getattr(msg, 'tool_calls', None)
                if tool_calls: 
                    last_call = tool_calls[-1]
                    return last_call.get('name') or ''

    return ''
    

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)