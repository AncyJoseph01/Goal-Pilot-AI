from pydantic import BaseModel, EmailStr
from typing import List
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: uuid.UUID
    email: EmailStr
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str