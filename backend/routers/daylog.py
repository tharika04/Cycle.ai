from datetime import date as date_type, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.daylog_model import DayTag
from backend.database import get_db
from backend.services.daylog import CATALOG, REVERSE, SYMPTOM_MAP, SYMPTOM_NAMES

router = APIRouter(prefix="/daylog", tags=["daylog"])


class DayIn(BaseModel):
    tags: Dict[str, List[str]] = {}
    severity: int = Field(default=3, ge=1, le=5)


@router.get("/catalog")
def catalog(user: models.User = Depends(get_current_user)):
    return {
        "categories": [{"key": k, "title": t, "tags": tags, "hint": h} for k, t, tags, h in CATALOG],
        "symptom_tags": list(SYMPTOM_MAP.keys()),
    }


@router.get("/dates")
def logged_dates(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    since = date_type.today() - timedelta(days=400)
    tag_days = {r[0] for r in db.query(DayTag.date).filter(DayTag.user_id == user.id, DayTag.date >= since)}
    sym_days = {r[0] for r in db.query(models.Symptom.date)
                .filter(models.Symptom.user_id == user.id, models.Symptom.date >= since)}
    return sorted(d.isoformat() for d in (tag_days | sym_days))


@router.get("/{day}")
def get_day(day: date_type, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    tags: Dict[str, List[str]] = {}
    for r in db.query(DayTag).filter_by(user_id=user.id, date=day).all():
        tags.setdefault(r.category, []).append(r.tag)

    severities = []
    for s in db.query(models.Symptom).filter_by(user_id=user.id, date=day).all():
        if s.symptom in REVERSE:
            cat, chip = REVERSE[s.symptom]
            bucket = tags.setdefault(cat, [])
            if chip not in bucket:
                bucket.append(chip)
            severities.append(s.severity or 3)
    severity = round(sum(severities) / len(severities)) if severities else 3
    return {"date": day.isoformat(), "tags": tags, "severity": min(5, max(1, severity))}


@router.put("/{day}")
def save_day(day: date_type, data: DayIn, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    clean: Dict[str, List[str]] = {}
    for key, _title, allowed, _hint in CATALOG:
        picked = []
        for t in data.tags.get(key, []):
            if t in allowed and t not in picked:
                picked.append(t)
        clean[key] = picked

    db.query(DayTag).filter_by(user_id=user.id, date=day).delete()
    for key, picked in clean.items():
        for t in picked:
            db.add(DayTag(user_id=user.id, date=day, category=key, tag=t))

    wanted = {SYMPTOM_MAP[t] for picked in clean.values() for t in picked if t in SYMPTOM_MAP}
    existing = db.query(models.Symptom).filter_by(user_id=user.id, date=day).all()
    for s in existing:
        if s.symptom in SYMPTOM_NAMES:
            if s.symptom in wanted:
                s.severity = data.severity
                wanted.discard(s.symptom)
            else:
                db.delete(s)
    for name in wanted:
        db.add(models.Symptom(user_id=user.id, date=day, symptom=name, severity=data.severity, mood=None))
    db.commit()
    return {"saved": True, "date": day.isoformat()}