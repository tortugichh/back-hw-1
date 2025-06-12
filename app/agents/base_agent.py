from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

class Message(BaseModel):
    id: str
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime
    message_type: str

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.message_history: List[Message] = []
    
    @abstractmethod
    async def process_message(self, message: Message) -> Message:
        """Process incoming message and return response"""
        pass
    
    def create_message(self, receiver: str, content: Dict[str, Any], message_type: str = "standard") -> Message:
        """Create a new message"""
        return Message(
            id=str(uuid.uuid4()),
            sender=self.name,
            receiver=receiver,
            content=content,
            timestamp=datetime.utcnow(),
            message_type=message_type
        )
    
    def add_to_history(self, message: Message):
        """Add message to history"""
        self.message_history.append(message)
    
    def get_conversation_context(self, limit: int = 10) -> List[Message]:
        """Get recent conversation context"""
        return self.message_history[-limit:]