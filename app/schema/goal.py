from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
import uuid
from enum import Enum

class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class StudySchedule(str, Enum):
    flexible = "flexible"
    regular = "regular"
    intensive = "intensive"

class LearningStyle(str, Enum):
    visual = "visual"
    reading = "reading"
    hands_on = "hands-on"
    mixed = "mixed"

class WeeklyScheduleItem(BaseModel):
    day: str = Field(description="Day of the week")
    topics: List[str] = Field(description="Topics to cover")
    duration: str = Field(description="Duration like '2h'")

class ResourceItem(BaseModel):
    type: str = Field(description="Resource type")
    title: str = Field(description="Resource title")
    duration: str = Field(description="Estimated duration")
    url: str = Field(description="Resource URL")

class MilestoneItem(BaseModel):
    week: int = Field(description="Week number")
    goal: str = Field(description="Milestone goal")
    completed: bool = Field(default=False)

class LearningPlan(BaseModel):
    weekly_schedule: List[WeeklyScheduleItem]
    resources: List[ResourceItem]
    milestones: List[MilestoneItem]

class AIPlanRequest(BaseModel):
    title: str
    description: str
    duration_days: int
    difficulty: Difficulty
    study_schedule: StudySchedule
    weekly_hours: str
    learning_style: LearningStyle

class GoalCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    duration_days: int
    start_date: Optional[date] = None     
    end_date: Optional[date] = None        
    difficulty: Difficulty
    study_schedule: StudySchedule
    weekly_hours: str
    learning_style: LearningStyle
    user_id: str

class Goal(GoalCreate):
    id: uuid.UUID
    weekly_schedule: List[WeeklyScheduleItem]
    resources: List[ResourceItem]
    milestones: List[MilestoneItem]
    progress: float = 0.0
    completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True