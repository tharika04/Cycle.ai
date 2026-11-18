from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.auth import get_current_user

router = APIRouter(prefix="/cycles", tags=["cycles"])

@router.post("", response_model=schemas.CycleOut)
def add_cycle(data: schemas.CycleCreate, db: Session = Depends(get_db),
              user: models.User = Depends(get_current_user)):
    if data.end_date and data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="End date is before start date")
    cycle = models.Cycle(user_id=user.id, **data.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle

@router.get("", response_model=List[schemas.CycleOut])
def list_cycles(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (db.query(models.Cycle).filter_by(user_id=user.id)
            .order_by(models.Cycle.start_date.desc()).all())

@router.put("/{cycle_id}", response_model=schemas.CycleOut)
def update_cycle(cycle_id: int, data: schemas.CycleUpdate, db: Session = Depends(get_db),
                 user: models.User = Depends(get_current_user)):
    cycle = db.query(models.Cycle).filter_by(id=cycle_id, user_id=user.id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cycle, key, value)
    db.commit()
    db.refresh(cycle)
    return cycle

@router.delete("/{cycle_id}")
def delete_cycle(cycle_id: int, db: Session = Depends(get_db),
                 user: models.User = Depends(get_current_user)):
    cycle = db.query(models.Cycle).filter_by(id=cycle_id, user_id=user.id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    db.delete(cycle)
    db.commit()
    return {"deleted": True}