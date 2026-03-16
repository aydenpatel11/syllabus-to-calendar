from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from enum import Enum


class EventType(str, Enum):
    """Types of academic events."""
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    DEADLINE = "deadline"
    READING = "reading"
    LECTURE = "lecture"
    DISCUSSION = "discussion"
    LAB = "lab"
    OTHER = "other"


class AcademicEvent(BaseModel):
    """Represents an academic event extracted from a syllabus."""
    
    title: str
    event_type: EventType
    start_date: date
    start_time: Optional[time] = None
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    is_all_day: bool = True
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurrence_exception_dates: Optional[list[date]] = None
    recurrence_exception_rules: Optional[list[str]] = None
