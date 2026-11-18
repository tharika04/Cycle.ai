from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models
from backend.database import get_db
from backend.auth import get_current_user
from backend.services.predictor import predict
from backend.services.nutrition import build_plan

router = APIRouter(prefix="/plan", tags=["plan"])

@router.get("")
def get_plan(phase: Optional[str] = None, diet: str = "vegetarian",
             db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if phase is None:
        cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
        phase = predict(cycles).get("current_phase", "follicular")
    try:
        return build_plan(phase, diet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))