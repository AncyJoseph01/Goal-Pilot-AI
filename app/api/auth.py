from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import uuid
from app.db import models
from app.db.database import database, engine
from sqlalchemy import insert, select, update
import os
import json

router = APIRouter()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_SECRETS_FILE = r"E:\Personal Project\Goal-Pilot-AI\app\credentials\client_secret.json"

# SCOPES: Gmail send, Calendar, profile, email, openid
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

@router.get("/google/login")
async def google_login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",   # request refresh token
        include_granted_scopes="true",
        prompt="consent"
    )
    # Save state somewhere if you want for security
    return RedirectResponse(authorization_url)

@router.get("/google/callback")
async def google_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # Serialize credentials to JSON so you can store them in DB
    creds_json = json.dumps({
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    })

    # Get user info
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info.get("email")
    name = user_info.get("name")

    # Save/update user in DB
    user_query = select(models.User).where(models.User.email == email)
    user = await database.fetch_one(user_query)

    if not user:
        user_id = str(uuid.uuid4())
        async with engine.begin() as conn:
            await conn.execute(
                insert(models.User),
                {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "google_linked": True,
                    "google_credentials": creds_json
                }
            )
    else:
        user_id = user["id"]
        async with engine.begin() as conn:
            await conn.execute(
                update(models.User)
                .where(models.User.id == user_id)
                .values(
                    google_linked=True,
                    google_credentials=creds_json
                )
            )

    # Temporary token (or your JWT)
    token = str(uuid.uuid4())
    redirect_url = f"http://localhost:3000/google-success?token={token}&email={email}&name={name}"
    return RedirectResponse(redirect_url)
