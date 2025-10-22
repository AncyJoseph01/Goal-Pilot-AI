from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, goals
from app.db.database import database

app = FastAPI(title="Goal Pilot AI", version="1.0.0")

# ✅ FIXED CORS - SPECIFIC ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # ✅ FRONTEND URLS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"message": "Goal Pilot AI - Learning Plans Powered by AI"}