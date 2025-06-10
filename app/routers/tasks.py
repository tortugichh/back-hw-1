from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import tasks as crud_tasks
from app.schemas import tasks as schemas_tasks
from app.database import SessionLocal, engine
from app.models import tasks as models_tasks

# Create database tables
models_tasks.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks/", response_model=schemas_tasks.Task)
def create_task(task: schemas_tasks.TaskCreate, db: Session = Depends(get_db)):
    return crud_tasks.create_task(db=db, task=task)

@router.get("/tasks/", response_model=List[schemas_tasks.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud_tasks.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas_tasks.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud_tasks.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/tasks/{task_id}", response_model=schemas_tasks.Task)
def update_task(task_id: int, task: schemas_tasks.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud_tasks.update_task(db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/tasks/{task_id}", response_model=schemas_tasks.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud_tasks.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
