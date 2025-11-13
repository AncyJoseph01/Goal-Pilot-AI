from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import uuid
from app.db import models
from app.db.database import database, engine
from sqlalchemy import insert, select
import os

router = APIRouter()

# Allow insecure transport (HTTP) for localhost testing
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Path to your Google OAuth client secret JSON
GOOGLE_CLIENT_SECRETS_FILE = r"E:\Personal Project\Goal-Pilot-AI\app\credentials\client_secret.json"

# Scopes your app needs
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# -------------------------------
# Step 1: Redirect user to Google for consent
# -------------------------------
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
    return RedirectResponse(authorization_url)

# -------------------------------
# Step 2: Handle Google redirect with "code"
# -------------------------------
@router.get("/google/callback")
async def google_callback(request: Request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    email = user_info.get("email")
    name = user_info.get("name")
    print("Google user:", email, name)

    # 1️⃣ Generate a temporary token (or real JWT if you implement)
    token = str(uuid.uuid4())  # Temporary placeholder

    # 2️⃣ Save user in DB if needed
    user_query = select(models.User).where(models.User.email == email)
    user = await database.fetch_one(user_query)
    if not user:
        # Create a new user
        user_id = str(uuid.uuid4())
        async with engine.begin() as conn:
            await conn.execute(
                insert(models.User),
                {"id": user_id, "email": email, "name": name}
            )
    else:
        user_id = user["id"]

    # 3️⃣ Redirect to frontend with token and email
    redirect_url = f"http://localhost:3000/google-success?token={token}&email={email}&name={name}"
    return RedirectResponse(redirect_url)
