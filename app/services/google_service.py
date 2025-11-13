from typing import List
from datetime import datetime, timedelta
import json
import logging

from sqlalchemy import select
from app.db.database import database
from app.db import models
from app.schema.google_schema import CalendarEventCreate
from app.services.google_utils import send_email, create_calendar_event

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from starlette.concurrency import run_in_threadpool

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ✅ Check if a user linked Google
async def is_google_linked(user_id: str) -> bool:
    user = await database.fetch_one(
        select(models.User.google_linked).where(models.User.id == user_id)
    )
    return bool(user and user["google_linked"])


# ✅ Retrieve user's Google credentials
async def get_user_credentials(user_id: str) -> Credentials | None:
    user = await database.fetch_one(select(models.User).where(models.User.id == user_id))
    if not user or not user.google_linked or not user.google_credentials:
        return None

    creds_data = json.loads(user.google_credentials)
    creds = Credentials.from_authorized_user_info(
        creds_data,
        scopes=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/gmail.send"
        ]
    )

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        await run_in_threadpool(creds.refresh, GoogleRequest())

    return creds


# ✅ Schedule milestone notifications — runs immediately
async def schedule_milestone_notifications(user_id: str, goal_title: str, milestones: List[dict]):
    """
    Immediately sends milestone reminders and creates Google Calendar events.
    Each milestone gets a unique timestamp so Google doesn't ignore duplicates.
    """

    # Check Google link
    if not await is_google_linked(user_id):
        logging.info(f"User {user_id} has not linked Google — skipping notifications.")
        return

    # Get credentials
    creds = await get_user_credentials(user_id)
    if not creds:
        logging.warning(f"No valid credentials for user {user_id} — skipping notifications.")
        return

    # Get user info
    user = await database.fetch_one(select(models.User).where(models.User.id == user_id))
    if not user:
        logging.error(f"User {user_id} not found in database.")
        return

    user_email = user["email"]

    # Process each milestone
    for idx, milestone in enumerate(milestones, start=1):
        try:
            goal_text = milestone.get("goal") or "Untitled milestone"
            milestone_date_str = milestone.get("date")

            # Prepare unique milestone time
            if milestone_date_str:
                milestone_date = datetime.strptime(milestone_date_str, "%Y-%m-%d")
            else:
                milestone_date = datetime.utcnow()

            # Each milestone is offset by +2 minutes from the previous one
            start_dt = datetime.utcnow() + timedelta(minutes=idx * 2)
            end_dt = start_dt + timedelta(hours=1)

            # === Send Email ===
            subject = f"Milestone Reminder: {goal_text} for {goal_title}"
            body = (
                f"Hi!\n\n"
                f"Here’s your milestone reminder:\n\n"
                f"Goal: {goal_title}\n"
                f"Milestone: {goal_text}\n"
                f"Scheduled: {start_dt.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Keep up the great work! 🎯"
            )

            await run_in_threadpool(send_email, creds, user_email, subject, body)
            logging.info(f"✅ Email sent for milestone '{goal_text}' to {user_email}")

            # === Create Google Calendar Event ===
            event_data = CalendarEventCreate(
                summary=f"Milestone: {goal_text}",
                description=f"Goal: {goal_title}",
                start_datetime=start_dt,
                end_datetime=end_dt,
            )

            await run_in_threadpool(create_calendar_event, creds, event_data)
            logging.info(f"✅ Calendar event created for milestone '{goal_text}'")

        except Exception as e:
            logging.error(f"❌ Failed to process milestone '{milestone.get('goal')}' — {e}")
