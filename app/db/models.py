import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, DateTime, Date, Enum, ForeignKey,
    Integer, Boolean, Float, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from enum import Enum as PyEnum
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)

    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # YOUR EXACT MISSING COLUMNS
    difficulty = Column(String(50), nullable=True)
    study_schedule = Column(String(50), nullable=True)
    weekly_hours = Column(String(10), nullable=True)
    learning_style = Column(String(50), nullable=True)
    weekly_schedule = Column(Text, nullable=True)    # JSON
    resources = Column(Text, nullable=True)          # JSON  
    milestones = Column(Text, nullable=True)         # JSON
    progress = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="goals")

    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
    summaries = relationship("Summary", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
    progress = relationship("Progress", back_populates="goal", uselist=False, cascade="all, delete-orphan", passive_deletes=True)

class TaskType(PyEnum):
    REMINDER = "reminder"
    TODO = "todo"
    EMAIL = "email"
    CALENDAR = "calendar"
    NOTION = "notion"
    GMEET = "gmeet"
    OTHER = "other"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(Enum(TaskType), nullable=False, default=TaskType.TODO)
    status = Column(String(50), default="yet_to_start")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
    goal = relationship("Goal", back_populates="tasks")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="tasks")

    resources = relationship("Resource", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)
    summaries = relationship("Summary", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    url = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)
    resource_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"))
    task = relationship("Task", back_populates="resources")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="summaries")

    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
    goal = relationship("Goal", back_populates="summaries")

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"))
    task = relationship("Task", back_populates="summaries")

    embedding = Column(Vector(768), nullable=True)

class Progress(Base):
    __tablename__ = "progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_progress = Column(Float, default=0.0)
    task_progress = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="progress_records")

    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
    goal = relationship("Goal", back_populates="progress")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="notifications")

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)


# class TaskType(PyEnum):
#     REMINDER = "reminder"
#     TODO = "todo"
#     EMAIL = "email"
#     CALENDAR = "calendar"
#     NOTION = "notion"
#     GMEET = "gmeet"
#     OTHER = "other"


# class Task(Base):
#     __tablename__ = "tasks"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     title = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     task_type = Column(Enum(TaskType), nullable=False, default=TaskType.TODO)
#     status = Column(String(50), default="yet_to_start")  # completed / in_progress / yet_to_start
#     due_date = Column(DateTime, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
#     goal = relationship("Goal", back_populates="tasks")

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
#     user = relationship("User", back_populates="tasks")

#     resources = relationship("Resource", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)
#     summaries = relationship("Summary", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)


# class Resource(Base):
#     __tablename__ = "resources"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     title = Column(String(255), nullable=True)
#     url = Column(Text, nullable=False)
#     source = Column(String(100), nullable=True)  # e.g., YouTube, Coursera, Google
#     difficulty = Column(String(50), nullable=True)
#     resource_type = Column(String(50), nullable=True)  # e.g., video, article, tutorial
#     created_at = Column(DateTime, default=datetime.utcnow)

#     task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"))
#     task = relationship("Task", back_populates="resources")


# class Summary(Base):
#     __tablename__ = "summaries"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     summary_type = Column(String(50), nullable=True)  # e.g., "goal_summary", "resource_summary"
#     description = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
#     user = relationship("User", back_populates="summaries")

#     goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
#     goal = relationship("Goal", back_populates="summaries")

#     task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"))
#     task = relationship("Task", back_populates="summaries")

#     embedding = Column(Vector(768), nullable=True)  # For LLM summarization or semantic search


# class Progress(Base):
#     __tablename__ = "progress"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     goal_progress = Column(Float, default=0.0)  # percentage
#     task_progress = Column(Float, default=0.0)
#     last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
#     user = relationship("User", back_populates="progress_records")

#     goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
#     goal = relationship("Goal", back_populates="progress")


# class Notification(Base):
#     __tablename__ = "notifications"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     message = Column(Text, nullable=False)
#     is_read = Column(Boolean, default=False)
#     notification_type = Column(String(50), nullable=True)  # e.g., reminder, deadline, motivational_tip
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
#     user = relationship("User", back_populates="notifications")

#     task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
#     goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True)