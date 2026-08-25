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


class Course(Base):
    """课程模块:一门课程挂在一个教材单元上,由多个课时(lesson)组成。"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cover_emoji = Column(String, nullable=True)
    order = Column(Integer, default=0)
    status = Column(String, default="active")

    lessons = relationship(
        "CourseLesson",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="CourseLesson.order",
    )
    unit = relationship("Unit")
    textbook = relationship("Textbook")


class CourseLesson(Base):
    """课时:content 为 JSON,包含有序的互动步骤列表(见 seed_courses.py 配置说明)。"""
    __tablename__ = "course_lessons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    order = Column(Integer, default=0)
    content = Column(JSON, nullable=False, default=dict)

    course = relationship("Course", back_populates="lessons")


class CourseProgress(Base):
    """上课进度:记录每个孩子每节课的完成状态和获得星星数。"""
    __tablename__ = "course_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("course_lessons.id"), nullable=False)
    stars = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
