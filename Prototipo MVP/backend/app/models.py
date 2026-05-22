from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    name       = Column(String(255), nullable=False)
    hashed_pw  = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tasks    = relationship("Task",        back_populates="user", cascade="all, delete-orphan")
    plans    = relationship("StudyPlan",   back_populates="user", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    exams    = relationship("Exam",        back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    text       = Column(String(500), nullable=False)
    subject    = Column(String(100))
    tag        = Column(String(50))
    done       = Column(Boolean, default=False)
    due_date   = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tasks")


class StudyPlan(Base):
    """
    Almacena el plan semanal generado por IA en formato JSONB.
    Estructura de 'plan_data':
    {
      "week_start": "2025-03-24",
      "days": [
        {
          "name": "Lunes",
          "slots": [
            { "time": "7:00–8:30", "subject": "Cálculo II", "tag": "Cálculo", "duration": 90 }
          ]
        }
      ]
    }
    """
    __tablename__ = "study_plans"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_data  = Column(JSONB, nullable=False)
    ai_prompt  = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="plans")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    role       = Column(String(20), nullable=False)   # "user" | "assistant"
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="messages")


class Exam(Base):
    """Examen o evaluación próxima del estudiante."""
    __tablename__ = "exams"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject    = Column(String(100), nullable=False)
    exam_date  = Column(DateTime(timezone=True), nullable=False)
    notes      = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="exams")
