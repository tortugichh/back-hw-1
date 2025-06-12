from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import Field

from app.agents.base_agent import BaseAgent, Message
from app.crud import tasks as crud_tasks
from app.models.tasks import Task
from app.database import SessionLocal

class TaskRetrievalTool(BaseTool):
    name: str = "get_tasks"
    description: str = "Retrieve tasks from the database based on filters"
    
    def _run(self, query: str = "", completed: Optional[bool] = None, limit: int = 100) -> List[Dict]:
        db = SessionLocal()
        try:
            tasks = crud_tasks.get_tasks(db, skip=0, limit=limit)
            
            # Filter by completion status if specified
            if completed is not None:
                tasks = [task for task in tasks if task.completed == completed]
            
            # Simple text search in title and description
            if query:
                query_lower = query.lower()
                tasks = [
                    task for task in tasks 
                    if query_lower in task.title.lower() or 
                    (task.description and query_lower in task.description.lower())
                ]
            
            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed
                }
                for task in tasks
            ]
        finally:
            db.close()


class TaskStatsTool(BaseTool):
    name: str = "get_task_stats"
    description: str = "Get statistics about tasks"
    
    def _run(self) -> Dict:
        db = SessionLocal()
        try:
            all_tasks = crud_tasks.get_tasks(db, skip=0, limit=1000)
            completed_tasks = [task for task in all_tasks if task.completed]
            pending_tasks = [task for task in all_tasks if not task.completed]
            
            return {
                "total_tasks": len(all_tasks),
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(pending_tasks),
                "completion_rate": len(completed_tasks) / len(all_tasks) * 100 if all_tasks else 0
            }
        finally:
            db.close()

class TaskRetrievalAgent(BaseAgent):
    # ...existing imports...

    def __init__(self, openai_api_key: str):
        super().__init__("TaskRetrievalAgent", "Agent responsible for retrieving and filtering task data")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=openai_api_key  # Changed from openai_api_key to api_key
        )
        
        self.tools = [TaskRetrievalTool(), TaskStatsTool()]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a task retrieval agent. Your job is to:
1. Understand user queries about tasks
2. Use available tools to retrieve relevant task information
3. Extract and structure the data for the response agent
4. Be precise and comprehensive in your data retrieval

Available tools:
- get_tasks: Retrieve tasks with optional filtering
- get_task_stats: Get overall task statistics

Always provide structured data that the response agent can use to answer user questions."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def process_message(self, message: Message) -> Message:
        """Process message and retrieve relevant task data"""
        try:
            user_query = message.content.get("query", "")
            
            # Use LangChain agent to process the query and retrieve data
            result = await self.agent_executor.ainvoke({"input": user_query})
            
            response_content = {
                "status": "success",
                "data": result.get("output", ""),
                "query_processed": user_query,
                "agent_type": "task_retrieval"
            }
            
        except Exception as e:
            response_content = {
                "status": "error",
                "error": str(e),
                "query_processed": message.content.get("query", ""),
                "agent_type": "task_retrieval"
            }
        
        response = self.create_message(
            receiver="ChatResponseAgent",
            content=response_content,
            message_type="data_response"
        )
        
        self.add_to_history(message)
        self.add_to_history(response)
        
        return response