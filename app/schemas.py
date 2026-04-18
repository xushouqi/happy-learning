from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


# --- Textbook ---
class TextbookResponse(BaseModel):
    id: int
    name: str
    source_path: Optional[str]
    cover_image: Optional[str]
    status: str

    class Config:
        from_attributes = True


class TextbookWithUnits(TextbookResponse):
    units: List["UnitResponse"]


# --- Unit ---
class UnitResponse(BaseModel):
    id: int
    textbook_id: int
    name: str
    order: int
    video_path: Optional[str]

    class Config:
        from_attributes = True


# --- VocabWord ---
class VocabWordResponse(BaseModel):
    id: int
    textbook_id: int
    unit_id: int
    word: str
    image_path: Optional[str]
    example_sentence: Optional[str]

    class Config:
        from_attributes = True


# --- Question ---
class QuestionResponse(BaseModel):
    id: int
    textbook_id: int
    unit_id: int
    type: str
    difficulty: int
    options: List
    answer: str
    image_url: Optional[str]
    audio_text: Optional[str]
    sentence: Optional[str]

    class Config:
        from_attributes = True


# --- Score ---
class ScoreCreate(BaseModel):
    user_id: int
    question_id: int
    correct: bool
    score: int


class ScoreResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    correct: bool
    score: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- DailyProgress ---
class DailyProgressCreate(BaseModel):
    user_id: int
    unit_id: int
    date: date
    total_score: int = 0
    completed: bool = False


class DailyProgressResponse(BaseModel):
    id: int
    user_id: int
    unit_id: int
    date: date
    total_score: int
    completed: bool

    class Config:
        from_attributes = True


# --- UnitProgress ---
class UnitProgressResponse(BaseModel):
    id: int
    user_id: int
    unit_id: int
    unit_name: str
    best_score: int
    total_questions: int
    attempts: int
    last_attempt: datetime
    completed: bool

    class Config:
        from_attributes = True


# --- User ---
class UserCreate(BaseModel):
    name: str
    avatar: str


class UserResponse(BaseModel):
    id: int
    name: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True
