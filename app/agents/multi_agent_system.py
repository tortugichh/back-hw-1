from typing import Dict, Any, List
import asyncio
from datetime import datetime

from app.agents.base_agent import BaseAgent, Message
from app.agents.task_retrieval_agent import TaskRetrievalAgent
from app.agents.chat_response_agent import ChatResponseAgent
from app.config import settings

class MultiAgentSystem:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.conversation_history: List[Message] = []
        self.active_conversations: Dict[str, List[Message]] = {}
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents in the system"""
        try:
            # Task Retrieval Agent
            self.agents["TaskRetrievalAgent"] = TaskRetrievalAgent(
                openai_api_key=settings.openai_api_key
            )
            
            # Chat Response Agent
            self.agents["ChatResponseAgent"] = ChatResponseAgent(
                openai_api_key=settings.openai_api_key
            )
            
            print("Multi-agent system initialized successfully")
        except Exception as e:
            print(f"Error initializing agents: {e}")
            raise
    
    async def process_user_query(self, user_query: str, conversation_id: str = "default") -> str:
        """
        Process user query through the multi-agent system
        
        Flow:
        1. User query → TaskRetrievalAgent
        2. TaskRetrievalAgent → ChatResponseAgent  
        3. ChatResponseAgent → User response
        """
        try:
            # Create initial user message
            user_message = Message(
                id=f"user_{datetime.utcnow().timestamp()}",
                sender="user",
                receiver="TaskRetrievalAgent",
                content={"query": user_query},
                timestamp=datetime.utcnow(),
                message_type="user_query"
            )
            
            # Add to conversation history
            if conversation_id not in self.active_conversations:
                self.active_conversations[conversation_id] = []
            
            self.active_conversations[conversation_id].append(user_message)
            self.conversation_history.append(user_message)
            
            # Step 1: Send to TaskRetrievalAgent
            task_agent = self.agents["TaskRetrievalAgent"]
            retrieval_response = await task_agent.process_message(user_message)
            
            self.active_conversations[conversation_id].append(retrieval_response)
            self.conversation_history.append(retrieval_response)
            
            # Step 2: Send TaskRetrievalAgent response to ChatResponseAgent
            chat_agent = self.agents["ChatResponseAgent"]
            final_response = await chat_agent.process_message(retrieval_response)
            
            self.active_conversations[conversation_id].append(final_response)
            self.conversation_history.append(final_response)
            
            # Return the final response text
            return final_response.content.get("response", "I'm sorry, I couldn't process your request.")
        
        except Exception as e:
            error_message = f"System error: {str(e)}"
            print(f"Error in process_user_query: {e}")
            return error_message
    
    def get_conversation_history(self, conversation_id: str = "default", limit: int = 10) -> List[Dict]:
        """Get conversation history for a specific conversation"""
        if conversation_id not in self.active_conversations:
            return []
        
        messages = self.active_conversations[conversation_id][-limit:]
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "receiver": msg.receiver,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": msg.message_type
            }
            for msg in messages
        ]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "agents": list(self.agents.keys()),
            "total_conversations": len(self.active_conversations),
            "total_messages": len(self.conversation_history),
            "system_status": "active"
        }
    
    async def reset_conversation(self, conversation_id: str):
        """Reset a specific conversation"""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
    
    async def shutdown(self):
        """Gracefully shutdown the multi-agent system"""
        print("Shutting down multi-agent system...")
        # Perform any cleanup operations here
        self.agents.clear()
        self.conversation_history.clear()
        self.active_conversations.clear()

# Global instance
multi_agent_system = MultiAgentSystem()