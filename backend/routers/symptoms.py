from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.auth import get_current_user

router = APIRouter(prefix="/symptoms", tags=["symptoms"])

@router.post("", response_model=schemas.SymptomOut)
def add_symptom(data: schemas.SymptomCreate, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    symptom = models.Symptom(user_id=user.id, **data.model_dump())
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    return symptom

@router.get("", response_model=List[schemas.SymptomOut])
def list_symptoms(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (db.query(models.Symptom).filter_by(user_id=user.id)
            .order_by(models.Symptom.date.desc()).all())