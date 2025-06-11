import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class ChatbotSettings(BaseModel):
    fastapi_base_url: str = os.getenv("FASTAPI_BASE_URL", "http://web:8000/api/v1")
    chatbot_username: str = os.getenv("CHATBOT_USERNAME", "chatbot_user")
    chatbot_password: str = os.getenv("CHATBOT_PASSWORD", "chatbot_password")
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

settings = ChatbotSettings() 