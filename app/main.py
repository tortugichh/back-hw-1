from fastapi import FastAPI
from app.routers import tasks

app = FastAPI(
    title="ToDo API",
    description="A simple ToDo application with FastAPI",
    version="1.0.0",
)

app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
