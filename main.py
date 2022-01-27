from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import SessionLocal, engine
from sqlalchemy.orm import  Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind = engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt= 0, lt= 6, description= "Priority must be between 1-5")
    complete: bool

    class Config():
        schema_extra = {
            "example":{
                "title": "This is test title for a Todo",
                "description": "This is a test description for a Todo",
                "priority": 5,
                "complete": False
            }
        }

@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()

@app.get("/todo/{todo_id}")
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .first()

    if todo_model is not None:
        return todo_model

    raise http_exception() 


@app.post("/")
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return success_reponse(201)

@app.put("/{todo_id}")
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
            .first()
    
    if todo_model is None:
        raise http_exception()
    
    todo_model.title = todo.title
    todo_model.description  = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return success_reponse(200)



@app.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
            .first()
    
    if todo_model is None:
        raise http_exception()
    
    db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
            .delete()
    
    db.commit()

    return success_reponse(200)

def success_reponse(status_code: int):
    return {
        "status": status_code,
        "transaction": "Successful"
    }

def http_exception():
    return HTTPException(status_code=404, detail= "Todo not found")