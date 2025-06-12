from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from llama_index.core import Document, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SimpleNodeParser
import json

from app.agents.base_agent import BaseAgent, Message

class ChatResponseAgent(BaseAgent):
    def __init__(self, openai_api_key: str):
        super().__init__("ChatResponseAgent", "Agent responsible for generating user-friendly responses")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # LlamaIndex for document processing and context enhancement
        self.llama_llm = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")
        
        self.system_prompt = """You are a helpful assistant for a ToDo application. Your role is to:

1. Provide friendly, conversational responses about tasks and productivity
2. Help users understand their task data in a clear and actionable way
3. Offer suggestions for task management and productivity improvement
4. Be concise but informative

When presenting task information:
- Use bullet points or numbered lists for multiple tasks
- Highlight important information like deadlines or completion status
- Provide context and insights, not just raw data
- Be encouraging and supportive about productivity

Always be helpful, friendly, and focused on the user's productivity goals."""
    
    def _create_context_documents(self, task_data: str) -> VectorStoreIndex:
        """Create LlamaIndex documents from task data for enhanced context"""
        try:
            # Parse task data if it's JSON
            if isinstance(task_data, str):
                try:
                    parsed_data = json.loads(task_data)
                    task_data = parsed_data
                except:
                    pass
            
            # Create documents from task data
            documents = []
            if isinstance(task_data, list):
                for task in task_data:
                    if isinstance(task, dict):
                        doc_text = f"Task: {task.get('title', 'No title')}\n"
                        doc_text += f"Description: {task.get('description', 'No description')}\n"
                        doc_text += f"Status: {'Completed' if task.get('completed', False) else 'Pending'}\n"
                        doc_text += f"ID: {task.get('id', 'Unknown')}"
                        documents.append(Document(text=doc_text))
            
            if not documents:
                documents.append(Document(text=str(task_data)))
            
            # Create vector index
            parser = SimpleNodeParser.from_defaults()
            nodes = parser.get_nodes_from_documents(documents)
            index = VectorStoreIndex(nodes, llm=self.llama_llm)
            
            return index
        except Exception as e:
            print(f"Error creating context documents: {e}")
            return None
    
    async def process_message(self, message: Message) -> Message:
        """Process message from TaskRetrievalAgent and generate user response"""
        try:
            message_content = message.content
            
            if message_content.get("status") == "error":
                response_text = f"I'm sorry, I encountered an error while retrieving your task information: {message_content.get('error', 'Unknown error')}"
            else:
                # Extract task data
                task_data = message_content.get("data", "")
                original_query = message_content.get("query_processed", "")
                
                # Create enhanced context using LlamaIndex
                index = self._create_context_documents(task_data)
                
                if index:
                    # Use LlamaIndex query engine for enhanced context
                    query_engine = index.as_query_engine(llm=self.llama_llm)
                    context_response = query_engine.query(f"Based on this task data, help answer: {original_query}")
                    enhanced_context = str(context_response)
                else:
                    enhanced_context = str(task_data)
                
                # Create prompt with context
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("human", f"""
User asked: {original_query}

Retrieved task data: {task_data}

Enhanced context: {enhanced_context}

Please provide a helpful, friendly response to the user's question about their tasks. 
Make it conversational and actionable, not just a data dump.
""")
                ])
                
                # Generate response
                response = await self.llm.ainvoke(prompt.format_messages())
                response_text = response.content
        
        except Exception as e:
            response_text = f"I apologize, but I encountered an error while processing your request: {str(e)}"
        
        # Create response message
        response_message = self.create_message(
            receiver="user",
            content={
                "response": response_text,
                "agent_type": "chat_response"
            },
            message_type="final_response"
        )
        
        self.add_to_history(message)
        self.add_to_history(response_message)
        
        return response_message