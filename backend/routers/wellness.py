import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.services.reminders import build_reminders, reminders_to_text, send_email
from backend.services.screening import screen

router = APIRouter(prefix="/wellness", tags=["wellness"])

_last_email = {}


def mask_email(email):
    name, _, domain = email.partition("@")
    return (name[:1] + "***@" + domain) if domain else "***"


@router.get("/screening")
def screening(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    symptoms = db.query(models.Symptom).filter_by(user_id=user.id).all()
    return screen(cycles, symptoms)


@router.get("/reminders")
def reminders(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    logs = db.query(models.DailyLog).filter_by(user_id=user.id).all()
    return {"reminders": build_reminders(cycles, logs), "email_hint": mask_email(user.email)}


@router.post("/reminders/email")
def email_reminders(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    now = time.time()
    if now - _last_email.get(user.id, 0) < 60:
        raise HTTPException(status_code=429, detail="Please wait a minute before sending another email.")
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    logs = db.query(models.DailyLog).filter_by(user_id=user.id).all()
    body = reminders_to_text(build_reminders(cycles, logs), user.name)
    try:
        send_email(user.email, "Your HerRhythm reminders", body)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail="Could not send the email: " + str(e)[:150])
    _last_email[user.id] = now
    return {"sent": True, "to": mask_email(user.email)}