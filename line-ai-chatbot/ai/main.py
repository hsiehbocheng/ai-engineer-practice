from fastapi import FastAPI
from chatbot import call_llm
from fastapi.responses import RedirectResponse
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/chat")
async def chat(query: str):
    response = call_llm([{"role": "user", "content": query}])
    
    return response
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)