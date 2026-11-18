from datetime import date as date_type
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.day_models import DayEntry

router = APIRouter(prefix="/day", tags=["day"])

SYNC_CATEGORIES = {"Symptoms", "Digestion and stool"}
SKIP_SYNC = {"everything is fine"}


def clean(text):
    return " ".join(str(text).split())[:40]


class CategoryIn(BaseModel):
    date: date_type
    category: str = Field(min_length=1, max_length=40)
    items: List[str] = Field(default_factory=list, max_length=60)
    severity: int = Field(default=3, ge=1, le=5)


@router.get("")
def get_day(day: date_type = Query(..., alias="date"), db: Session = Depends(get_db),
            user: models.User = Depends(get_current_user)):
    rows = db.query(DayEntry).filter_by(user_id=user.id, date=day).all()
    selections = {}
    for r in rows:
        selections.setdefault(r.category, []).append(r.item)
    names = {i.lower() for c in SYNC_CATEGORIES for i in selections.get(c, [])}
    symptoms = db.query(models.Symptom).filter(
        models.Symptom.user_id == user.id, models.Symptom.date == day
    ).all()
    severity = next((s.severity for s in symptoms if s.symptom in names), 3)
    return {"date": day.isoformat(), "selections": selections, "severity": severity}


@router.put("/category")
def save_category(data: CategoryIn, db: Session = Depends(get_db),
                  user: models.User = Depends(get_current_user)):
    category = clean(data.category)
    items = list(dict.fromkeys(clean(i) for i in data.items if clean(i)))

    query = db.query(DayEntry).filter_by(user_id=user.id, date=data.date, category=category)
    old = [r.item for r in query.all()]
    query.delete(synchronize_session=False)
    for item in items:
        db.add(DayEntry(user_id=user.id, date=data.date, category=category, item=item))

    if category in SYNC_CATEGORIES:
        touched = {i.lower() for i in old + items}
        if touched:
            db.query(models.Symptom).filter(
                models.Symptom.user_id == user.id,
                models.Symptom.date == data.date,
                models.Symptom.symptom.in_(touched),
            ).delete(synchronize_session=False)
        for item in items:
            if item.lower() not in SKIP_SYNC:
                db.add(models.Symptom(user_id=user.id, date=data.date, symptom=item.lower(),
                                      severity=data.severity, mood=None))
    db.commit()
    return {"saved": True, "count": len(items)}


@router.get("/logged")
def logged_days(start: date_type, end: date_type, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    if (end - start).days > 400 or end < start:
        raise HTTPException(status_code=400, detail="Invalid date range")
    a = db.query(DayEntry.date).filter(
        DayEntry.user_id == user.id, DayEntry.date >= start, DayEntry.date <= end
    ).distinct().all()
    b = db.query(models.Symptom.date).filter(
        models.Symptom.user_id == user.id, models.Symptom.date >= start, models.Symptom.date <= end
    ).distinct().all()
    days = {r[0] for r in a} | {r[0] for r in b}
    return sorted(d.isoformat() for d in days)