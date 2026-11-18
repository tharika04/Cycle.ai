from datetime import date as date_type, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.services.forecast import build_forecast

router = APIRouter(prefix="/daily", tags=["daily"])

MOODS = ["happy", "calm", "tired", "anxious", "irritable", "sad"]


class DailyIn(BaseModel):
    date: date_type
    water_glasses: Optional[int] = Field(default=None, ge=0, le=30)
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    exercise_minutes: Optional[int] = Field(default=None, ge=0, le=600)
    energy: Optional[int] = Field(default=None, ge=1, le=5)
    stress: Optional[int] = Field(default=None, ge=1, le=5)
    mood: Optional[str] = None


def serialize(row):
    return {
        "date": row.date.isoformat(),
        "water_glasses": row.water_glasses,
        "sleep_hours": row.sleep_hours,
        "exercise_minutes": row.exercise_minutes,
        "energy": row.energy,
        "stress": row.stress,
        "mood": row.mood,
    }


@router.post("")
def save_daily(data: DailyIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    row = db.query(models.DailyLog).filter_by(user_id=user.id, date=data.date).first()
    if row is None:
        row = models.DailyLog(user_id=user.id, date=data.date)
        db.add(row)
    row.water_glasses = data.water_glasses
    row.sleep_hours = data.sleep_hours
    row.exercise_minutes = data.exercise_minutes
    row.energy = data.energy
    row.stress = data.stress
    row.mood = data.mood if data.mood in MOODS else None
    db.commit()
    return serialize(row)


@router.get("")
def list_daily(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    since = date_type.today() - timedelta(days=120)
    rows = (db.query(models.DailyLog).filter(models.DailyLog.user_id == user.id, models.DailyLog.date >= since)
            .order_by(models.DailyLog.date.asc()).all())
    return [serialize(r) for r in rows]


@router.get("/forecast")
def forecast(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    logs = db.query(models.DailyLog).filter_by(user_id=user.id).all()
    return build_forecast(cycles, logs)