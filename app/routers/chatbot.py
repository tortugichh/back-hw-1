from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid

from app.dependencies import get_current_user
from app.models.users import User
from app.agents.multi_agent_system import multi_agent_system

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]

class SystemStatus(BaseModel):
    agents: List[str]
    total_conversations: int
    total_messages: int
    system_status: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Main chat endpoint for interacting with the multi-agent system
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{current_user.id}_{uuid.uuid4().hex[:8]}"
        
        # Process the user query through the multi-agent system
        response = await multi_agent_system.process_user_query(
            user_query=request.message,
            conversation_id=conversation_id
        )
        
        from datetime import datetime
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/history/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for a specific conversation
    """
    try:
        messages = multi_agent_system.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )

@router.delete("/chat/history/{conversation_id}")
async def reset_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Reset/clear a specific conversation
    """
    try:
        await multi_agent_system.reset_conversation(conversation_id)
        return {"message": f"Conversation {conversation_id} has been reset"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting conversation: {str(e)}"
        )

@router.get("/chat/status", response_model=SystemStatus)
async def get_system_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current status of the multi-agent system
    """
    try:
        status_info = multi_agent_system.get_agent_status()
        return SystemStatus(**status_info)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system status: {str(e)}"
        )

@router.post("/chat/suggestions")
async def get_chat_suggestions(
    current_user: User = Depends(get_current_user)
):
    """
    Get suggested questions/commands for the chatbot
    """
    suggestions = [
        "Show me all my tasks",
        "How many tasks do I have completed?",
        "What are my pending tasks?",
        "Show me task statistics",
        "Find tasks with 'important' in the title",
        "What tasks are due soon?",
        "Show me my productivity summary",
        "Help me organize my tasks"
    ]
    
    return {"suggestions": suggestions}

# WebSocket endpoint for real-time chat (optional)
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/chat/ws")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    Note: This is a simplified version. In production, you'd want to add authentication.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id", f"ws_{uuid.uuid4().hex[:8]}")
            
            # Process through multi-agent system
            response = await multi_agent_system.process_user_query(
                user_query=user_message,
                conversation_id=conversation_id
            )
            
            # Send response back to client
            response_data = {
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.send_message(json.dumps(response_data), websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)