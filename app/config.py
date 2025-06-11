import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    openai_api_key: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
