from pydantic import BaseModel
from datetime import datetime

class CalendarEventCreate(BaseModel):
    summary: str
    description: str = None
    start_datetime: datetime
    end_datetime: datetime

class EmailMessageCreate(BaseModel):
    to: str
    subject: str
    body: str
