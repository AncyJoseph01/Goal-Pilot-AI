from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
from datetime import datetime
from app.db import models, database
import json
import asyncio
from app.schema.google_schema import CalendarEventCreate, EmailMessageCreate

# -------------------------------
# Google Calendar
# -------------------------------
async def create_calendar_event(credentials: Credentials, event_data: CalendarEventCreate):
    """Create a Google Calendar event asynchronously"""
    def _create_event():
        service = build("calendar", "v3", credentials=credentials)
        event = {
            "summary": event_data.summary,
            "description": event_data.description,
            "start": {"dateTime": event_data.start_datetime.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event_data.end_datetime.isoformat(), "timeZone": "UTC"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60*24},
                    {"method": "popup", "minutes": 60}
                ]
            }
        }
        return service.events().insert(calendarId="primary", body=event).execute()

    return await asyncio.to_thread(_create_event)

# -------------------------------
# Gmail
# -------------------------------
async def send_email(credentials: Credentials, to: str, subject: str, body: str):
    """Send a Gmail email asynchronously"""
    def _send():
        service = build("gmail", "v1", credentials=credentials)
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw}
        return service.users().messages().send(userId="me", body=message_body).execute()

    return await asyncio.to_thread(_send)

# -------------------------------
# Milestone Email
# -------------------------------
async def send_milestone_email(user_id: str, milestone_goal: str, goal_title: str):
    """Send a milestone reminder email"""
    user_query = await database.fetch_one(
        models.User.__table__.select().where(models.User.id == user_id)
    )
    if not user_query or not user_query.get("google_credentials"):
        print(f"No Google credentials for user {user_id}, skipping email")
        return

    creds_data = json.loads(user_query["google_credentials"])
    creds = Credentials.from_authorized_user_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )

    subject = f"Reminder: Milestone '{milestone_goal}' for '{goal_title}'"
    body = f"Hi! This is a reminder for your milestone:\n\nGoal: {goal_title}\nMilestone: {milestone_goal}\nDate: {datetime.utcnow().date()}"
    
    sent = await send_email(creds, user_query["email"], subject, body)
    print(f"Email sent to {user_query['email']} for milestone {milestone_goal}")
    return sent
