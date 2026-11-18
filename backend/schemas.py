from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str
    age: Optional[int] = None
    email: str
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    name: str
    age: Optional[int]
    email: str
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CycleCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_level: str = "medium"

class CycleUpdate(BaseModel):
    end_date: Optional[date] = None
    flow_level: Optional[str] = None

class CycleOut(CycleCreate):
    id: int
    model_config = {"from_attributes": True}

class SymptomCreate(BaseModel):
    date: date
    symptom: str
    severity: int = Field(ge=1, le=5)
    mood: Optional[str] = None

class SymptomOut(SymptomCreate):
    id: int
    model_config = {"from_attributes": True}