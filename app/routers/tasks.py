from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.crud import tasks as crud_tasks
from app.schemas import tasks as schemas_tasks
from app.database import get_db, engine
from app.models import tasks as models_tasks
from app.dependencies import get_current_user
from app.models.users import User
from app.cache import get_redis_client
from app.tasks import debug_task # Import the Celery task

# Create database tables (This should ideally be handled by Alembic in production)
models_tasks.Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.post("/tasks/", response_model=schemas_tasks.Task)
def create_task(task: schemas_tasks.TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_tasks.create_task(db=db, task=task)

@router.get("/tasks/", response_model=List[schemas_tasks.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), redis_client = Depends(get_redis_client)):
    # Try to get tasks from Redis cache
    cache_key = f"tasks:{skip}:{limit}"
    cached_tasks = redis_client.get(cache_key)

    if cached_tasks:
        return [schemas_tasks.Task.model_validate_json(task) for task in json.loads(cached_tasks)]

    # If not in cache, get from database
    tasks = crud_tasks.get_tasks(db, skip=skip, limit=limit)
    
    # Store in Redis cache (e.g., for 60 seconds)
    if tasks:
        redis_client.setex(cache_key, 60, json.dumps([task.model_dump_json() for task in tasks]))

    return tasks

@router.post("/send-task/{word}")
async def send_task(word: str, current_user: User = Depends(get_current_user)):
    debug_task.delay(word)
    return {"message": f"Task to process '{word}' dispatched to Celery."}

@router.get("/tasks/{task_id}", response_model=schemas_tasks.Task)
def read_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = crud_tasks.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/tasks/{task_id}", response_model=schemas_tasks.Task)
def update_task(task_id: int, task: schemas_tasks.TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = crud_tasks.update_task(db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/tasks/{task_id}", response_model=schemas_tasks.Task)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = crud_tasks.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
