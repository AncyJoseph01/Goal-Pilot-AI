# app/api/goals.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
from datetime import datetime
import json
import logging

from sqlalchemy import insert, select
from app.db.database import database, engine
from app.db import models
from app.schema.goal import Goal, GoalCreate, AIPlanRequest, LearningPlan
from app.services.google_service import schedule_milestone_notifications, get_user_credentials, is_google_linked
from app.services.google_utils import send_email

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from datetime import timedelta

router = APIRouter()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# -------------------------------
# LLM Setup
# -------------------------------
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY, temperature=0.7)
output_parser = JsonOutputParser(pydantic_object=LearningPlan)


# -------------------------------
# Goal Endpoints
# -------------------------------

@router.post("/", response_model=Goal)
async def create_goal(goal: GoalCreate, background_tasks: BackgroundTasks):
    """
    Create a new goal with AI-generated learning plan.
    Sends welcome email and schedules milestones if Google is linked.
    """

    # 1️⃣ Validate user
    user = await database.fetch_one(select(models.User).where(models.User.id == goal.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    duration_days = int(goal.duration_days)

    # 2️⃣ Generate AI Plan
    ai_plan = await generate_ai_plan_openai(
        title=goal.title,
        description=goal.description,
        duration_days=duration_days,
        start_date=goal.start_date,
        end_date=goal.end_date,
        difficulty=goal.difficulty,
        study_schedule=goal.study_schedule,
        weekly_hours=goal.weekly_hours,
        learning_style=goal.learning_style
    )

    goal_id = uuid.uuid4()
    created_at = datetime.utcnow()

    # 3️⃣ Save goal in database
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

    # 4️⃣ Send welcome email and schedule milestones if Google linked
    if await is_google_linked(goal.user_id):
        creds = await get_user_credentials(goal.user_id)
        if creds:
            # Welcome email
            subject = f"Welcome! Your Learning Plan for '{goal.title}'"
            body = f"Hi! Your learning plan for '{goal.title}' is ready.\nCheck your milestones and weekly schedule."
            background_tasks.add_task(send_email, creds, user["email"], subject, body)

            # Compute exact dates for milestones
            start_date_obj = goal.start_date
            if isinstance(start_date_obj, str):
                start_date_obj = datetime.strptime(start_date_obj, "%Y-%m-%d")
            for milestone in ai_plan["milestones"]:
                milestone_date = start_date_obj + timedelta(weeks=milestone["week"] - 1)
                milestone["date"] = milestone_date.strftime("%Y-%m-%d")

            # Schedule milestones in background
            background_tasks.add_task(
                schedule_milestone_notifications, goal.user_id, goal.title, ai_plan["milestones"]
            )

    # 5️⃣ Return saved goal
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
    """
    Get all goals for a user, optional search by title.
    """
    query = select(models.Goal).where(models.Goal.user_id == user_id)
    if q:
        query = query.where(models.Goal.title.ilike(f"%{q}%"))

    rows = await database.fetch_all(query)
    goals = []

    for row in rows:
        data = dict(row)
        data["weekly_schedule"] = json.loads(data.get("weekly_schedule") or "[]")
        data["resources"] = json.loads(data.get("resources") or "[]")
        data["milestones"] = json.loads(data.get("milestones") or "[]")
        goals.append(Goal(**{**data, "user_id": str(data["user_id"])}))

    return goals


@router.post("/ai-plan", response_model=LearningPlan)
async def generate_ai_plan_preview(request: AIPlanRequest):
    """
    Generate AI Learning Plan Preview.
    """
    try:
        return await generate_ai_plan_openai(
            title=request.title,
            description=request.description,
            duration_days=request.duration_days,
            start_date=None,
            end_date=None,
            difficulty=request.difficulty,
            study_schedule=request.study_schedule,
            weekly_hours=request.weekly_hours,
            learning_style=request.learning_style
        )
    except Exception as e:
        logging.error(f"OpenAI Error: {e}")
        return get_fallback_plan(request.title, request.weekly_hours, request.duration_days)


# -------------------------------
# AI Plan Generation
# -------------------------------
async def generate_ai_plan_openai(title, description, duration_days, start_date, end_date, difficulty, study_schedule, weekly_hours, learning_style):
    prompt = PromptTemplate(
        template="""You are an expert learning coach. Generate a detailed learning plan.

Goal: {title}
Description: {description}
Duration: {duration_days} days
Start Date: {start_date}
End Date: {end_date}
Difficulty: {difficulty}
Study Schedule: {study_schedule}
Weekly Hours: {weekly_hours}
Learning Style: {learning_style}

Include:
1. Weekly schedule with topics, tasks, and durations
2. Curated resources with links and durations
3. Milestones with step-by-step instructions
4. Only valid JSON output

{format_instructions}""",
        input_variables=[
            "title","description","duration_days","start_date","end_date",
            "difficulty","study_schedule","weekly_hours","learning_style"
        ],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )

    chain = prompt | llm | output_parser
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else "TBD"
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else "TBD"

    return await chain.ainvoke({
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


# -------------------------------
# Fallback Plan
# -------------------------------
def get_fallback_plan(title, weekly_hours, duration_days):
    hours_per_session = max(1, int(weekly_hours) // 3)
    weeks = max(1, duration_days // 7)

    return {
        "weekly_schedule": [
            {"day": f"Week 1 - Monday", "topics": [f"{title} Basics"], "duration": f"{hours_per_session}h"},
            {"day": f"Week 1 - Wednesday", "topics": ["Practice Exercises"], "duration": f"{hours_per_session}h"},
            {"day": f"Week 1 - Friday", "topics": ["Review & Assessment"], "duration": f"{hours_per_session}h"}
        ],
        "resources": [
            {"type": "Video", "title": f"{title} Crash Course", "duration": "2h", "url": f"https://youtube.com/results?search_query={title.replace(' ','+')}"}
        ],
        "milestones": [
            {"week": 1, "goal": f"Complete {title} Basics", "completed": False},
            {"week": max(2, weeks // 2), "goal": f"Intermediate {title} Project", "completed": False},
            {"week": weeks, "goal": f"Master Advanced {title} Concepts", "completed": False}
        ]
    }
