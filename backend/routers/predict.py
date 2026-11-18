from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import models
from backend.database import get_db
from backend.auth import get_current_user
from backend.services.predictor import predict

router = APIRouter(prefix="/predict", tags=["predict"])

@router.get("")
def get_prediction(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    return predict(cycles)