from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import tasks, auth, chatbot  # Add chatbot import

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI application...")
    yield
    # Shutdown
    print("Shutting down FastAPI application...")

app = FastAPI(
    title="ToDo API",
    description="A simple ToDo application with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])  # Add this line

@app.get("/")
async def root():
    return {
        "message": "Welcome to ToDo API", 
        "version": "1.0.0",
        "features": [
            "Task management",
            "User authentication",
            "Chatbot interface"  # Add this feature
        ]
    }