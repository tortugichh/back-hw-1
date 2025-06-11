import requests
from langchain.tools import Tool
from typing import List, Dict, Any
from auth_handler import auth_handler
from config import settings
import json

FASTAPI_BASE_URL = settings.fastapi_base_url

def _create_task(description: str, due_date: str = None) -> str:
    """Creates a new task in the ToDo application.
    Args:
        description (str): The description of the task.
        due_date (str, optional): The due date of the task in YYYY-MM-DD format. Defaults to None.
    """
    payload = {"description": description}
    if due_date:
        payload["due_date"] = due_date
    
    headers = auth_handler.get_authorized_headers()
    try:
        response = requests.post(f"{FASTAPI_BASE_URL}/tasks/", json=payload, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error creating task: {e}"

def _list_tasks(skip: int = 0, limit: int = 100) -> str:
    """Lists all tasks in the ToDo application.
    Args:
        skip (int, optional): The number of items to skip (for pagination). Defaults to 0.
        limit (int, optional): The maximum number of items to return. Defaults to 100.
    """
    headers = auth_handler.get_authorized_headers()
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/tasks/?skip={skip}&limit={limit}", headers=headers)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error listing tasks: {e}"

def _update_task(task_id: int, description: str = None, completed: bool = None, due_date: str = None) -> str:
    """Updates an existing task in the ToDo application.
    Args:
        task_id (int): The ID of the task to update.
        description (str, optional): The new description of the task. Defaults to None.
        completed (bool, optional): Whether the task is completed. Defaults to None.
        due_date (str, optional): The new due date of the task in YYYY-MM-DD format. Defaults to None.
    """
    payload = {}
    if description is not None:
        payload["description"] = description
    if completed is not None:
        payload["completed"] = completed
    if due_date is not None:
        payload["due_date"] = due_date

    if not payload:
        return "No fields provided to update the task."
    
    headers = auth_handler.get_authorized_headers()
    try:
        response = requests.put(f"{FASTAPI_BASE_URL}/tasks/{task_id}", json=payload, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error updating task: {e}"

def _delete_task(task_id: int) -> str:
    """Deletes a task from the ToDo application.
    Args:
        task_id (int): The ID of the task to delete.
    """
    headers = auth_handler.get_authorized_headers()
    try:
        response = requests.delete(f"{FASTAPI_BASE_URL}/tasks/{task_id}", headers=headers)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error deleting task: {e}"


fastapi_tools = [
    Tool(
        name="CreateTask",
        func=_create_task,
        description="""Use this tool to create a new task. 
        Input should be a JSON string with 'description' (string) and optionally 'due_date' (string in YYYY-MM-DD format). 
        Example input: {\"description\": \"Call mom\", \"due_date\": \"2023-12-31\"}"""
    ),
    Tool(
        name="ListTasks",
        func=_list_tasks,
        description="""Use this tool to list all tasks. 
        Input can be an empty string, or a JSON string with optional 'skip' (integer) and 'limit' (integer) for pagination. 
        Example input: {\"skip\": 0, \"limit\": 10}"""
    ),
    Tool(
        name="UpdateTask",
        func=_update_task,
        description="""Use this tool to update an existing task. 
        Input should be a JSON string with 'task_id' (integer) and at least one of 'description' (string), 'completed' (boolean), or 'due_date' (string in YYYY-MM-DD format). 
        Example input: {\"task_id\": 1, \"completed\": true}"""
    ),
    Tool(
        name="DeleteTask",
        func=_delete_task,
        description="""Use this tool to delete a task. 
        Input should be an integer representing the 'task_id' of the task to delete. 
        Example input: 1"""
    ),
] 