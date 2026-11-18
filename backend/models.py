from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, Text
from backend.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)


class Cycle(Base):
    __tablename__ = "cycles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    flow_level = Column(String, default="medium")  # light / medium / heavy


class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(Date, nullable=False)
    symptom = Column(String, nullable=False)
    severity = Column(Integer, default=1)  # 1-5
    mood = Column(String, nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    conversation_id = Column(String, nullable=True)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DailyLog(Base):
    __tablename__ = "daily_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(Date, nullable=False)
    water_glasses = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    energy = Column(Integer, nullable=True)  # 1-5
    stress = Column(Integer, nullable=True)  # 1-5
    mood = Column(String, nullable=True)