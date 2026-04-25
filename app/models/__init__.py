from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scores = relationship("Score", back_populates="user")
    daily_progress = relationship("DailyProgress", back_populates="user")
    unit_progress = relationship("UnitProgress", back_populates="user")


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    source_path = Column(String, nullable=True)
    cover_image = Column(String, nullable=True)
    status = Column(String, default="active")

    units = relationship("Unit", back_populates="textbook", cascade="all, delete-orphan")
    vocab_words = relationship("VocabWord", back_populates="textbook", cascade="all, delete-orphan")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    video_path = Column(String, nullable=True)

    textbook = relationship("Textbook", back_populates="units")
    questions = relationship("Question", back_populates="unit", cascade="all, delete-orphan")
    vocab_words = relationship("VocabWord", back_populates="unit")


class VocabWord(Base):
    __tablename__ = "vocab_words"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    word = Column(String, nullable=False)
    image_path = Column(String, nullable=True)
    example_sentence = Column(String, nullable=True)

    textbook = relationship("Textbook", back_populates="vocab_words")
    unit = relationship("Unit", back_populates="vocab_words")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    type = Column(String, nullable=False)  # image_select_word, image_select_sentence, listen_select, listen_spell, listen_spell_sentence, image_listen_spell_sentence
    difficulty = Column(Integer, default=1)  # 1-3
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    audio_text = Column(String, nullable=True)
    sentence = Column(String, nullable=True)

    textbook = relationship("Textbook")
    unit = relationship("Unit", back_populates="questions")
    scores = relationship("Score", back_populates="question")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    correct = Column(Boolean, nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scores")
    question = relationship("Question", back_populates="scores")


class DailyProgress(Base):
    __tablename__ = "daily_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_score = Column(Integer, default=0)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="daily_progress")


class UnitProgress(Base):
    __tablename__ = "unit_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    best_score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="unit_progress")
    unit = relationship("Unit")
