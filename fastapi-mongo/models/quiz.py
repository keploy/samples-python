# app/models/quiz.py

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


class EndQuizRequest(BaseModel):
    name: str


class QuizStart(BaseModel):
    password: int
    name: str


class AnswerSubmission(BaseModel):
    name: str
    answers: List[str]


# Question model to represent individual question details
class Question(BaseModel):
    question: str
    choice_A: str
    choice_B: str
    choice_C: str
    choice_D: str
    answer: str  # Should be one of "A", "B", "C", or "D"
    is_correct: Optional[bool] = False


# QuizCreate model – input from client
class QuizCreate(BaseModel):
    name: str
    subject: str
    num_questions: int
    # trigger_link: HttpUrl
    # questions: List[Question]
    topic: str
    difficulty_level: int


class QuestionUpdate(BaseModel):
    question: str
    choice_A: str
    choice_B: str
    choice_C: str
    choice_D: str
    answer: str
    is_correct: bool


# Main Quiz model – includes fields auto-populated by backend
class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    subject: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now(IST))
    metadata_fields: Optional[dict] = Field(default_factory=dict)
    trigger_link: HttpUrl
    taken_by: List[str]
    num_questions: int
    questions: List[Question]
    user_responses: List[dict]
    is_started: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    exec_time: Optional[float] = None  # in seconds
    topic: str
    difficulty_level: int
    password: int
    is_executed: bool = False

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
        populate_by_name = True
