import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.services.chatbot import (
    CRISIS_MESSAGE, MEDICAL_WARNING, build_context, find_flag, generate_reply,
)
from backend.services.predictor import predict

router = APIRouter(prefix="/chat", tags=["chat"])

LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"]


def clean_id(value):
    """Safe conversation id, or None for the old (legacy) chat."""
    if value and value != "legacy" and re.fullmatch(r"[A-Za-z0-9-]{1,64}", value):
        return value
    return None


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = "English"
    conversation_id: str = ""


@router.post("")
def chat(data: ChatIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    flag = find_flag(data.message)
    language = data.language if data.language in LANGUAGES else "English"
    cid = clean_id(data.conversation_id)

    if flag == "crisis":
        reply = CRISIS_MESSAGE
    else:
        cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
        symptoms = (db.query(models.Symptom).filter_by(user_id=user.id)
                    .order_by(models.Symptom.date.desc()).limit(15).all())
        history = (db.query(models.ChatHistory).filter_by(user_id=user.id, conversation_id=cid)
                   .order_by(models.ChatHistory.id.desc()).limit(2).all())[::-1]
        context = build_context(predict(cycles), symptoms)
        context += "\nThe user chose the reply language: " + language + ". Always reply in " + language + "."
        try:
            answer = generate_reply(data.message + "\n\n[Reply only in " + language + "]", history, context)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            if flag == "medical":
                answer = ""
            else:
                raise HTTPException(status_code=502, detail="AI service error: " + str(e)[:200])
        reply = (MEDICAL_WARNING + "\n\n" + answer).strip() if flag == "medical" else answer

    db.add(models.ChatHistory(user_id=user.id, conversation_id=cid, message=data.message, response=reply))
    db.commit()
    return {"response": reply, "flag": flag}


@router.get("/conversations")
def conversations(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = (db.query(models.ChatHistory).filter_by(user_id=user.id)
            .order_by(models.ChatHistory.id.asc()).all())
    found = {}
    for r in rows:
        key = r.conversation_id or "legacy"
        if key not in found:
            found[key] = {"id": key, "title": (r.message or "")[:40], "last": r.id}
        found[key]["last"] = r.id
    return sorted(found.values(), key=lambda c: c["last"], reverse=True)[:20]


@router.get("/history")
def history(conversation_id: str = "", db: Session = Depends(get_db),
            user: models.User = Depends(get_current_user)):
    if not conversation_id:
        return []
    cid = clean_id(conversation_id)
    rows = (db.query(models.ChatHistory).filter_by(user_id=user.id, conversation_id=cid)
            .order_by(models.ChatHistory.id.desc()).limit(50).all())[::-1]
    return [{"message": r.message, "response": r.response} for r in rows]


@router.delete("/history")
def delete_chat(conversation_id: str = "", db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    if not conversation_id:
        return {"deleted": False}
    cid = clean_id(conversation_id)
    db.query(models.ChatHistory).filter_by(user_id=user.id, conversation_id=cid).delete()
    db.commit()
    return {"deleted": True}