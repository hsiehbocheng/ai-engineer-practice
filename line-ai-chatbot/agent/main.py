from fastapi import FastAPI
from chatbot import call_llm
from test_mcp import main as call_llm_with_mcp
from fastapi.responses import RedirectResponse
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/chat")
async def chat(query: str):
    response = await call_llm_with_mcp([{"role": "user", "content": query}])
    response = response['messages'][-1].content
    
    return response
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)