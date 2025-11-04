# from fastapi import APIRouter, HTTPException
# from google.oauth2.credentials import Credentials
# from app.services.google_service import create_calendar_event, send_email, send_milestone_email
# from app.schema.google_schema import CalendarEventCreate, EmailMessageCreate
# from app.db import database, models
# import json

# router = APIRouter()

# # -------------------------------
# # Helper to load user Google credentials
# # -------------------------------
# async def get_user_credentials(user_id: str) -> Credentials:
#     user_query = await database.fetch_one(
#         models.User.__table__.select().where(models.User.id == user_id)
#     )
#     if not user_query or not user_query.get("google_credentials"):
#         return None
#     creds_data = json.loads(user_query["google_credentials"])
#     return Credentials.from_authorized_user_info(
#         creds_data,
#         scopes=[
#             "https://www.googleapis.com/auth/calendar",
#             "https://www.googleapis.com/auth/gmail.send"
#         ]
#     )

# # -------------------------------
# # Endpoints
# # -------------------------------
# @router.post("/calendar-event")
# async def add_calendar_event(user_id: str, event: CalendarEventCreate):
#     creds = await get_user_credentials(user_id)
#     if not creds:
#         raise HTTPException(status_code=400, detail="No Google credentials for user")
#     created_event = await create_calendar_event(creds, event)
#     return created_event

# @router.post("/send-email")
# async def send_user_email(user_id: str, email_data: EmailMessageCreate):
#     creds = await get_user_credentials(user_id)
#     if not creds:
#         raise HTTPException(status_code=400, detail="No Google credentials for user")
#     sent_message = await send_email(creds, email_data.to, email_data.subject, email_data.body)
#     return sent_message

# @router.post("/send-milestone-email/{user_id}")
# async def send_milestone_reminder(user_id: str, milestone_goal: str, goal_title: str):
#     """Send a milestone reminder email immediately (useful for testing)"""
#     sent = await send_milestone_email(user_id, milestone_goal, goal_title)
#     if not sent:
#         raise HTTPException(status_code=400, detail="Failed to send milestone email")
#     return {"status": "sent", "milestone": milestone_goal, "goal": goal_title}
