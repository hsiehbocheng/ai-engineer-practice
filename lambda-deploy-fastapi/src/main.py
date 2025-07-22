from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum
from typing import List, Optional
from datetime import datetime

# FastAPI 應用程式
app = FastAPI(title="Simple Todo API", version="1.0.0")

# Lambda handler (用於 AWS Lambda 部署)
handler = Mangum(app)

# 資料模型
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime

# 記憶體存儲（簡單起見，不使用資料庫）
todos_db = []
todo_id_counter = 1

@app.get("/")
async def root():
    return {"message": "Todo API is running!", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "todo-api", "todos_count": len(todos_db)}

# GET - 獲取所有 todos
@app.get("/todos", response_model=List[Todo])
async def get_todos():
    return todos_db

# GET - 獲取特定 todo
@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    todo = next((t for t in todos_db if t["id"] == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# POST - 建立新 todo
@app.post("/todos", response_model=Todo)
async def create_todo(todo: TodoCreate):
    global todo_id_counter
    
    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "completed": False,
        "created_at": datetime.now()
    }
    
    todos_db.append(new_todo)
    todo_id_counter += 1
    
    return new_todo

# PUT - 更新 todo
@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    todo_index = next((i for i, t in enumerate(todos_db) if t["id"] == todo_id), None)
    
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # 更新欄位
    if todo_update.title is not None:
        todos_db[todo_index]["title"] = todo_update.title
    if todo_update.description is not None:
        todos_db[todo_index]["description"] = todo_update.description
    if todo_update.completed is not None:
        todos_db[todo_index]["completed"] = todo_update.completed
    
    return todos_db[todo_index]

# DELETE - 刪除 todo
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    todo_index = next((i for i, t in enumerate(todos_db) if t["id"] == todo_id), None)
    
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    deleted_todo = todos_db.pop(todo_index)
    return {"message": "Todo deleted successfully", "deleted_todo": deleted_todo}

# 本地開發時的啟動函數
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)