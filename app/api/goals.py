from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import date, datetime
import json

from app.db.database import database, engine
from app.db import models
from app.schema.goal import Goal, GoalCreate, AIPlanRequest, LearningPlan
from sqlalchemy import insert, select, update, delete

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings

router = APIRouter()

# ✅ AI LLM Setup
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY, temperature=0.7)
output_parser = JsonOutputParser(pydantic_object=LearningPlan)

@router.post("/", response_model=Goal)
async def create_goal(goal: GoalCreate):
    """Create a new goal with AI-generated learning plan"""
    # Check if user exists
    user_query = select(models.User).where(models.User.id == goal.user_id)
    user = await database.fetch_one(user_query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    duration_days = int(goal.duration_days)

    # Generate AI plan
    ai_plan = await generate_ai_plan_openai(
        goal.title, goal.description, duration_days, 
        goal.start_date, goal.end_date, goal.difficulty,
        goal.study_schedule, goal.weekly_hours, goal.learning_style
    )

    goal_id = uuid.uuid4()
    created_at = datetime.utcnow()

    async with engine.begin() as conn:
        await conn.execute(
            insert(models.Goal),
            {
                "id": goal_id,
                "title": goal.title,
                "description": goal.description,
                "duration_days": duration_days,
                "start_date": goal.start_date,
                "end_date": goal.end_date,
                "created_at": created_at,
                "difficulty": goal.difficulty,
                "study_schedule": goal.study_schedule,
                "weekly_hours": goal.weekly_hours,
                "learning_style": goal.learning_style,
                "weekly_schedule": json.dumps(ai_plan["weekly_schedule"]),
                "resources": json.dumps(ai_plan["resources"]),
                "milestones": json.dumps(ai_plan["milestones"]),
                "progress": 0.0,
                "completed": False,
                "user_id": goal.user_id
            }
        )

    # RETURN SAVED GOAL
    return Goal(
        id=goal_id,
        title=goal.title,
        description=goal.description,
        duration_days=duration_days,
        start_date=goal.start_date,
        end_date=goal.end_date,
        created_at=created_at,
        difficulty=goal.difficulty,
        study_schedule=goal.study_schedule,
        weekly_hours=goal.weekly_hours,
        learning_style=goal.learning_style,
        weekly_schedule=ai_plan["weekly_schedule"],
        resources=ai_plan["resources"],
        milestones=ai_plan["milestones"],
        progress=0.0,
        completed=False,
        user_id=goal.user_id
    )

@router.get("/", response_model=List[Goal])
async def read_goals(user_id: str, q: str = None):
    """Get all goals for a user, with optional search."""
    query = select(models.Goal).where(models.Goal.user_id == user_id)
    
    if q:
        query = query.where(models.Goal.title.ilike(f"%{q}%"))  # Search filter
    
    rows = await database.fetch_all(query)
    
    goals = []
    for row in rows:
        goal_data = dict(row)
        goal_data["weekly_schedule"] = json.loads(row.weekly_schedule) if row.weekly_schedule else []
        goal_data["resources"] = json.loads(row.resources) if row.resources else []
        goal_data["milestones"] = json.loads(row.milestones) if row.milestones else []
        goals.append(Goal(**{**goal_data, "user_id": str(goal_data["user_id"])}))
    
    return goals

@router.post("/ai-plan", response_model=LearningPlan)
async def generate_ai_plan(request: AIPlanRequest):
    """🤖 Generate AI Learning Plan (Step 3 Preview)"""
    try:
        # Try OpenAI first
        ai_plan = await generate_ai_plan_openai(
            request.title, request.description, request.duration_days,
            None, None, request.difficulty, request.study_schedule,
            request.weekly_hours, request.learning_style
        )
        return ai_plan
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return get_fallback_plan(request.title, request.weekly_hours, request.duration_days)

async def generate_ai_plan_openai(title, description, duration_days, start_date, end_date, difficulty, study_schedule, weekly_hours, learning_style):
    """Generate AI plan using OpenAI"""
    prompt = PromptTemplate(
        template="""You are an expert learning plan generator. Create a detailed, personalized learning plan.

Learning Goal: {title}
Description: {description}
Duration: {duration_days} days
Start Date: {start_date}
End Date: {end_date}
Difficulty Level: {difficulty}
Study Schedule: {study_schedule}
Weekly Hours Available: {weekly_hours}
Preferred Learning Style: {learning_style}

Generate a comprehensive learning plan with:
1. A weekly schedule with specific days, topics, and durations
2. Curated learning resources (courses, videos, books, articles) with real URLs when possible
3. Progressive milestones to track learning progress

{format_instructions}

Provide ONLY valid JSON output. No additional text or explanations.""",
        input_variables=["title", "description", "duration_days", "start_date", "end_date", 
                        "difficulty", "study_schedule", "weekly_hours", "learning_style"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )
    
    chain = prompt | llm | output_parser
    
    # ✅ PERFECT FIX: Handle Optional dates
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else "TBD"
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "TBD"
    
    result = await chain.ainvoke({
        "title": title,
        "description": description,
        "duration_days": duration_days,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "difficulty": difficulty,
        "study_schedule": study_schedule,
        "weekly_hours": weekly_hours,
        "learning_style": learning_style
    })
    return result

def get_fallback_plan(title, weekly_hours, duration_days):
    """Fallback plan if OpenAI fails"""
    hours_per_session = max(1, int(weekly_hours) // 3)
    weeks = max(1, duration_days // 7)
    
    return {
        "weekly_schedule": [
            {"day": f"Week 1 - Monday", "topics": [f"{title} Basics", "Fundamental Concepts"], "duration": f"{hours_per_session}h"},
            {"day": f"Week 1 - Wednesday", "topics": ["Practice Exercises", "Hands-on Projects"], "duration": f"{hours_per_session}h"},
            {"day": f"Week 1 - Friday", "topics": ["Weekly Review", "Progress Assessment"], "duration": f"{hours_per_session}h"}
        ],
        "resources": [
            {"type": "Video", "title": f"{title} Crash Course", "duration": "2h", "url": f"https://youtube.com/results?search_query={title.replace(' ', '+')}+tutorial"},
            {"type": "Article", "title": f"{title} Official Guide", "duration": "1h", "url": f"https://www.google.com/search?q={title.replace(' ', '+')}+guide"},
            {"type": "Project", "title": f"Build {title} App", "duration": "3h", "url": f"https://github.com/search?q={title}"}
        ],
        "milestones": [
            {"week": 1, "goal": f"Complete {title} Fundamentals", "completed": False},
            {"week": max(2, weeks // 2), "goal": f"Build Intermediate {title} Project", "completed": False},
            {"week": weeks, "goal": f"Master Advanced {title} Concepts", "completed": False}
        ]
    }