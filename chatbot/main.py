import os
import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

app = FastAPI()

# Pydantic models mirroring app/schemas/tasks.py
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    completed: bool = False

    class Config:
        from_attributes = True

class ChatbotRequest(BaseModel):
    message: str

class ChatbotResponse(BaseModel):
    response: str

# Configuration from environment variables
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
CHATBOT_USERNAME = os.getenv("CHATBOT_USERNAME", "chatbot_user")
CHATBOT_PASSWORD = os.getenv("CHATBOT_PASSWORD", "chatbot_password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Global variable to store the access token (for simplicity, in a real app use a proper token management)
access_token: Optional[str] = None

async def get_access_token():
    global access_token
    if access_token:
        return access_token

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FASTAPI_BASE_URL}/api/v1/auth/token",
                data={"username": CHATBOT_USERNAME, "password": CHATBOT_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]
            return access_token
        except httpx.HTTPStatusError as e:
            print(f"Error authenticating: {e.response.text}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chatbot authentication failed")
        except httpx.RequestError as e:
            print(f"Network error during authentication: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cannot connect to main API for authentication")

# Langchain setup
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant that helps manage tasks.
            You can understand requests to add or delete tasks.
            When asked to add a task, identify the task title and an optional description.
            When asked to delete a task, identify the task ID.
            If the user asks to add a task but doesn't provide a title, ask for it.
            If the user asks to delete a task but doesn't provide an ID, ask for it.
            Your output should be a JSON object with 'action' (add_task, delete_task, get_tasks, none) and 'details' (a dictionary containing title, description, or task_id).
            Example add_task: {{"action": "add_task", "details": {{"title": "Buy groceries", "description": "Milk, eggs, bread"}}}}
            Example delete_task: {{"action": "delete_task", "details": {{"task_id": 123}}}}
            Example get_tasks: {{"action": "get_tasks", "details": {{}}}}
            Example none: {{"action": "none", "details": {{"response": "I didn't understand that. Please specify if you want to add or delete a task."}}}}
            If the user asks to list tasks, set the action to "get_tasks".
            """,
        ),
        ("human", "{message}"),
    ]
)

parser = JsonOutputParser()

chain = prompt | llm | parser

@app.post("/chat", response_model=ChatbotResponse)
async def chat_with_bot(request: ChatbotRequest):
    try:
        parsed_output = await chain.invoke({"message": request.message})
        action = parsed_output.get("action")
        details = parsed_output.get("details", {})

        access_token_val = await get_access_token()
        headers = {"Authorization": f"Bearer {access_token_val}"}

        async with httpx.AsyncClient() as client:
            if action == "add_task":
                title = details.get("title")
                if not title:
                    return ChatbotResponse(response="Please provide a title for the task you want to add.")
                
                description = details.get("description")
                task_data = {"title": title}
                if description:
                    task_data["description"] = description
                
                response = await client.post(
                    f"{FASTAPI_BASE_URL}/api/v1/tasks/",
                    json=task_data,
                    headers=headers
                )
                response.raise_for_status()
                new_task = Task(**response.json())
                return ChatbotResponse(response=f"Task '{new_task.title}' (ID: {new_task.id}) has been added.")

            elif action == "delete_task":
                task_id = details.get("task_id")
                if task_id is None:
                    return ChatbotResponse(response="Please provide the ID of the task you want to delete.")
                
                try:
                    task_id = int(task_id) # Ensure task_id is an integer
                except ValueError:
                    return ChatbotResponse(response="Invalid task ID. Please provide a number.")

                response = await client.delete(
                    f"{FASTAPI_BASE_URL}/api/v1/tasks/{task_id}",
                    headers=headers
                )
                response.raise_for_status()
                return ChatbotResponse(response=f"Task with ID {task_id} has been deleted.")

            elif action == "get_tasks":
                response = await client.get(
                    f"{FASTAPI_BASE_URL}/api/v1/tasks/",
                    headers=headers
                )
                response.raise_for_status()
                tasks = [Task(**task_data) for task_data in response.json()]
                if not tasks:
                    return ChatbotResponse(response="You have no tasks.")
                
                task_list_str = "\n".join([f"- ID: {task.id}, Title: {task.title}, Completed: {task.completed}" for task in tasks])
                return ChatbotResponse(response=f"Here are your tasks:\n{task_list_str}")

            elif action == "none":
                return ChatbotResponse(response=details.get("response", "I didn't understand that. Please specify if you want to add or delete a task."))
            
            else:
                return ChatbotResponse(response="I'm not sure how to handle that request. Please try rephrasing.")

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        detail = e.response.json().get("detail", "An unknown error occurred with the main API.")
        return ChatbotResponse(response=f"Error interacting with the task API: {detail} (Status: {status_code})")
    except httpx.RequestError as e:
        return ChatbotResponse(response=f"Network error when connecting to the main API: {e}")
    except Exception as e:
        return ChatbotResponse(response=f"An unexpected error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Chatbot service is running!"} 