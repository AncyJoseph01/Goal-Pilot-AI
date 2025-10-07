from pydantic import BaseModel, EmailStr
import uuid


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
