from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from sqlalchemy import insert, select, update, delete
from passlib.context import CryptContext

# ✅ STABLE PASSWORD HASHING
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from app.db import models
from app.db.database import database
from app.schema.user import User, UserCreate, LoginRequest

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    normalized_email = user.email.lower()
    
    # Check if user exists
    query = select(models.User).where(models.User.email.ilike(normalized_email))
    existing_user = await database.fetch_one(query)
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ GENERATE UUID DIRECTLY (FIX!)
    user_id = uuid.uuid4()
    safe_password = user.password[:72]
    hashed_password = pwd_context.hash(safe_password)
    
    await database.execute(
        insert(models.User).values(
            id=user_id,  # ✅ USE DIRECT UUID
            email=normalized_email,
            password=hashed_password
        )
    )

    return User(
        id=user_id,  # ✅ RETURN DIRECT UUID
        email=normalized_email,
    )

@router.get("/", response_model=List[User])
async def read_users():
    query = select(models.User)
    rows = await database.fetch_all(query)
    return [User(id=row.id, email=row.email) for row in rows]

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: uuid.UUID):
    query = select(models.User).where(models.User.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(id=user.id, email=user.email)

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: uuid.UUID, updated_user: UserCreate):
    query = select(models.User).where(models.User.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    safe_password = updated_user.password[:72]
    q = (
        update(models.User)
        .where(models.User.id == user_id)
        .values(
            email=updated_user.email.lower(), 
            password=pwd_context.hash(safe_password)
        )
    )
    await database.execute(q)

    return User(id=user_id, email=updated_user.email.lower())

@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID):
    query = select(models.User).where(models.User.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    q = delete(models.User).where(models.User.id == user_id)
    await database.execute(q)

    return {"message": "User deleted successfully"}

@router.post("/login", response_model=User)
async def login_user(request: LoginRequest):
    normalized_email = request.email.lower()
    query = select(models.User).where(models.User.email.ilike(normalized_email))
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    safe_password = request.password[:72]
    if not pwd_context.verify(safe_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return User(id=user.id, email=user.email)