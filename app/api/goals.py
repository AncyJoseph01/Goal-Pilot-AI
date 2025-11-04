from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
from datetime import datetime
import json
import asyncio

from app.db.database import database, engine
from app.db import models
from app.schema.goal import Goal, GoalCreate, AIPlanRequest, LearningPlan
from sqlalchemy import insert, select

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings

from app.services.google_service import send_email, create_calendar_event
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from datetime import timedelta
import logging

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# -------------------------------
# AI LLM Setup
# -------------------------------
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY, temperature=0.7)
output_parser = JsonOutputParser(pydantic_object=LearningPlan)

async def is_google_linked(user_id: str) -> bool:
    user_query = await database.fetch_one(
        select(models.User.google_linked).where(models.User.id == user_id)
    )
    return bool(user_query and user_query["google_linked"])

# -------------------------------
# Get user credentials
# -------------------------------
async def get_user_credentials(user_id: str) -> Credentials | None:
    user_query = await database.fetch_one(
        select(models.User).where(models.User.id == user_id)
    )
    if not user_query or not user_query.google_linked:
        return None

    creds_json = user_query.google_credentials
    if not creds_json:
        return None

    creds_data = json.loads(creds_json)
    creds = Credentials.from_authorized_user_info(
        creds_data,
        scopes=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/gmail.send"
        ]
    )

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
    return creds

# -------------------------------
# Background: Milestone Emails & Calendar
# -------------------------------
async def schedule_milestone_notifications(user_id: str, goal_title: str, milestones: list):
    if not await is_google_linked(user_id):
        logging.info(f"User {user_id} has not linked Google, skipping milestone notifications")
        return

    creds = await get_user_credentials(user_id)
    if not creds:
        logging.warning(f"No valid credentials for user {user_id}, skipping notifications")
        return

    user_query = await database.fetch_one(select(models.User).where(models.User.id == user_id))
    user_email = user_query["email"]

    for idx, milestone in enumerate(milestones, start=1):
        try:
            logging.info(f"Processing milestone {idx}/{len(milestones)}: {milestone['goal']}")

            # Send milestone email
            subject = f"Milestone Reminder: {milestone['goal']} for {goal_title}"
            body = (
                f"Hi!\n\nReminder for your milestone:\n"
                f"Goal: {goal_title}\n"
                f"Milestone: {milestone['goal']}\n"
                f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
                "Keep up the great work!"
            )
            await send_email(creds, to=user_email, subject=subject, body=body)
            logging.info(f"✅ Sent milestone email: {milestone['goal']} to {user_email}")

            # Add milestone to Google Calendar
            from app.schema.google_schema import CalendarEventCreate
            start_datetime = datetime.utcnow()
            end_datetime = start_datetime + timedelta(hours=1)
            event_data = CalendarEventCreate(
                summary=f"Milestone: {milestone['goal']}",
                description=f"Goal: {goal_title}",
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            await create_calendar_event(creds, event_data)
            logging.info(f"✅ Added milestone to Google Calendar: {milestone['goal']}")

        except Exception as e:
            logging.error(f"❌ Failed milestone '{milestone['goal']}' for user {user_id}: {e}")
# -------------------------------
# Create Goal Endpoint
# -------------------------------
@router.post("/", response_model=Goal)
async def create_goal(goal: GoalCreate, background_tasks: BackgroundTasks):
    """Create a new goal with AI-generated learning plan, optionally send emails/calendar events"""
    
    # 1️⃣ Check if user exists
    user_query = await database.fetch_one(select(models.User).where(models.User.id == goal.user_id))
    if not user_query:
        raise HTTPException(status_code=404, detail="User not found")
    
    duration_days = int(goal.duration_days)
    
    # 2️⃣ Generate AI learning plan
    ai_plan = await generate_ai_plan_openai(
        goal.title, goal.description, duration_days,
        goal.start_date, goal.end_date, goal.difficulty,
        goal.study_schedule, goal.weekly_hours, goal.learning_style
    )
    
    goal_id = uuid.uuid4()
    created_at = datetime.utcnow()
    
    # 3️⃣ Save goal to database
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
    
    # Get user email
    user_email = user_query["email"]

    # 4️⃣ Send welcome email & schedule milestones only if Google linked
    if await is_google_linked(goal.user_id):
        creds = await get_user_credentials(goal.user_id)
        if creds:
            subject = f"Welcome! Your Learning Plan for '{goal.title}'"
            body = f"Hi! Your learning plan for '{goal.title}' has been created.\nCheck milestones and weekly schedule."
            
            # Use user_email instead of creds.email
            background_tasks.add_task(send_email, creds, user_email, subject, body)
            
            # Schedule milestone notifications
            background_tasks.add_task(schedule_milestone_notifications, goal.user_id, goal.title, ai_plan["milestones"])
    
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


# -------------------------------
# Get all goals
# -------------------------------
@router.get("/", response_model=List[Goal])
async def read_goals(user_id: str, q: str = None):
    """Get all goals for a user, with optional search."""
    query = select(models.Goal).where(models.Goal.user_id == user_id)
    
    if q:
        query = query.where(models.Goal.title.ilike(f"%{q}%"))
    
    rows = await database.fetch_all(query)
    
    goals = []
    for row in rows:
        goal_data = dict(row)
        goal_data["weekly_schedule"] = json.loads(row.weekly_schedule) if row.weekly_schedule else []
        goal_data["resources"] = json.loads(row.resources) if row.resources else []
        goal_data["milestones"] = json.loads(row.milestones) if row.milestones else []
        goals.append(Goal(**{**goal_data, "user_id": str(goal_data["user_id"])}))
    
    return goals

# -------------------------------
# AI Plan Preview Endpoint
# -------------------------------
@router.post("/ai-plan", response_model=LearningPlan)
async def generate_ai_plan(request: AIPlanRequest):
    """🤖 Generate AI Learning Plan (Step 3 Preview)"""
    try:
        ai_plan = await generate_ai_plan_openai(
            request.title, request.description, request.duration_days,
            None, None, request.difficulty, request.study_schedule,
            request.weekly_hours, request.learning_style
        )
        return ai_plan
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return get_fallback_plan(request.title, request.weekly_hours, request.duration_days)

# -------------------------------
# AI Plan generation function
# -------------------------------
async def generate_ai_plan_openai(title, description, duration_days, start_date, end_date, difficulty, study_schedule, weekly_hours, learning_style):
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

# -------------------------------
# Fallback plan
# -------------------------------
def get_fallback_plan(title, weekly_hours, duration_days):
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