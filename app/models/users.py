from typing import Optional
from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# Pydantic models for user creation and response
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserInDB(UserCreate):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None 