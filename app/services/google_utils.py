# app/services/google_utils.py
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import logging
from email.mime.text import MIMEText
from datetime import datetime


def send_email(creds: Credentials, to: str, subject: str, body: str):
    """
    Sends an email using the Gmail API (real API call).
    """
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Create the email
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        # Encode to base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send email
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        logging.info(f"✅ Email sent to {to} (message id: {sent_message.get('id')})")

    except Exception as e:
        logging.error(f"❌ Failed to send email to {to}: {e}")


def create_calendar_event(creds: Credentials, event_data):
    """
    Adds an event to Google Calendar (real API call).
    """
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            "summary": event_data.summary,
            "description": event_data.description,
            "start": {"dateTime": event_data.start_datetime.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event_data.end_datetime.isoformat(), "timeZone": "UTC"},
        }

        created_event = service.events().insert(
            calendarId='primary', body=event
        ).execute()

        logging.info(f"✅ Added event to Google Calendar: {created_event.get('htmlLink')}")

    except Exception as e:
        logging.error(f"❌ Failed to create calendar event '{event_data.summary}': {e}")
