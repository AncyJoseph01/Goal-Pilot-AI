# app/services/google_service.py
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def is_google_linked(user_id: str) -> bool:
    user = await database.fetch_one(select(models.User.google_linked).where(models.User.id == user_id))
    return bool(user and user["google_linked"])


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

    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
    return creds


async def schedule_milestone_notifications(user_id: str, goal_title: str, milestones: List[dict]):
    if not await is_google_linked(user_id):
        logging.info(f"User {user_id} has not linked Google, skipping milestone notifications")
        return

    creds = await get_user_credentials(user_id)
    if not creds:
        logging.warning(f"No valid credentials for user {user_id}, skipping notifications")
        return

    user = await database.fetch_one(select(models.User).where(models.User.id == user_id))
    user_email = user["email"]

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
            await send_email(creds, user_email, subject, body)

            # Add milestone to Google Calendar
            start_dt = datetime.utcnow()
            end_dt = start_dt + timedelta(hours=1)
            event_data = CalendarEventCreate(
                summary=f"Milestone: {milestone['goal']}",
                description=f"Goal: {goal_title}",
                start_datetime=start_dt,
                end_datetime=end_dt
            )
            await create_calendar_event(creds, event_data)

        except Exception as e:
            logging.error(f"❌ Failed milestone '{milestone['goal']}' for user {user_id}: {e}")
