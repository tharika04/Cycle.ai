from collections import Counter, defaultdict
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import Base, get_db
from backend.services.predictor import predict

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/me")
def me(user: models.User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "age": user.age, "email": user.email}


def _phase_for(day, pred):
    ovulation_day = pred["avg_cycle_length"] - 14
    if day <= pred["avg_period_length"]:
        return "menstrual"
    if day < ovulation_day - 1:
        return "follicular"
    if day <= ovulation_day + 1:
        return "ovulation"
    return "luteal"


def symptom_insights(cycles, symptoms, pred):
    """Per-symptom count, average severity and the phase it shows up in most."""
    starts = sorted(c.start_date for c in cycles)
    groups = defaultdict(list)
    for s in symptoms:
        earlier = [d for d in starts if d <= s.date]
        if not earlier:
            continue
        day = (s.date - earlier[-1]).days + 1
        if day > 60:
            continue
        groups[s.symptom].append((s.severity, _phase_for(day, pred)))
    out = []
    for name, rows in groups.items():
        phases = Counter(p for _, p in rows)
        top, top_n = phases.most_common(1)[0]
        out.append({
            "symptom": name,
            "count": len(rows),
            "avg_severity": round(sum(sev for sev, _ in rows) / len(rows), 1),
            "top_phase": top,
            "top_phase_share": round(100 * top_n / len(rows)),
            "by_phase": dict(phases),
        })
    return sorted(out, key=lambda r: r["count"], reverse=True)


@router.get("/insights")
def insights(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    symptoms = db.query(models.Symptom).filter_by(user_id=user.id).all()
    pred = predict(cycles)
    if pred.get("status") != "ok":
        return {"status": "no_data", "message": "Log your first period to see insights."}
    return {"status": "ok", "prediction": pred, "symptoms": symptom_insights(cycles, symptoms, pred)}


@router.get("/report")
def report(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    from fpdf import FPDF

    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    symptoms = db.query(models.Symptom).filter_by(user_id=user.id).all()
    pred = predict(cycles)

    def clean(text):
        return str(text).encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def heading(text):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, clean(text), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)

    def line(text):
        pdf.multi_cell(0, 6, clean(text), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "HerRhythm Health Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    line("Name: " + user.name)
    line("Generated on " + date.today().isoformat())

    if pred.get("status") == "ok":
        heading("Cycle summary")
        line("Cycles logged: " + str(pred["cycles_logged"]))
        line("Average cycle length: " + str(pred["avg_cycle_length"]) + " days")
        line("Average period length: " + str(pred["avg_period_length"]) + " days")
        line("Last period start: " + str(pred["last_period_start"]))
        line("Predicted next period: " + str(pred["next_period_start"]))
        line("Regularity: " + ("irregular pattern noticed" if pred["irregular"] else "no irregularity noticed"))
        line("Prediction confidence: " + str(pred["confidence"]))

        heading("Logged periods (most recent first)")
        for c in sorted(cycles, key=lambda x: x.start_date, reverse=True)[:12]:
            end = c.end_date.isoformat() if c.end_date else "ongoing"
            line(c.start_date.isoformat() + " to " + end + " | flow: " + (c.flow_level or "-"))

        heading("Symptom patterns")
        rows = symptom_insights(cycles, symptoms, pred)
        if rows:
            for r in rows:
                line("- " + r["symptom"].title() + ": logged " + str(r["count"]) + " time(s), average severity "
                     + str(r["avg_severity"]) + "/5, most often in the " + r["top_phase"] + " phase ("
                     + str(r["top_phase_share"]) + "% of entries).")
        else:
            line("No symptoms logged.")
    else:
        heading("Cycle summary")
        line("No periods logged yet.")

    heading("Note")
    line("This summary is generated from self-reported data in HerRhythm. "
         "It is not a diagnosis. Please discuss any concerns with a doctor.")

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="herrhythm_report.pdf"'},
    )


@router.get("/export")
def export_data(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    cycles = db.query(models.Cycle).filter_by(user_id=user.id).all()
    symptoms = db.query(models.Symptom).filter_by(user_id=user.id).all()
    chats = db.query(models.ChatHistory).filter_by(user_id=user.id).all()
    dailies = db.query(models.DailyLog).filter_by(user_id=user.id).all()
    return {
        "profile": {"name": user.name, "age": user.age, "email": user.email},
        "cycles": [
            {
                "start_date": c.start_date.isoformat(),
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "flow_level": c.flow_level,
            }
            for c in cycles
        ],
        "symptoms": [
            {"date": s.date.isoformat(), "symptom": s.symptom, "severity": s.severity, "mood": s.mood}
            for s in symptoms
        ],
        "daily_logs": [
            {
                "date": d.date.isoformat(),
                "water_glasses": d.water_glasses,
                "sleep_hours": d.sleep_hours,
                "exercise_minutes": d.exercise_minutes,
                "energy": d.energy,
                "stress": d.stress,
                "mood": d.mood,
            }
            for d in dailies
        ],
        "chat_history": [
            {
                "message": r.message,
                "response": r.response,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in chats
        ],
    }


@router.delete("")
def delete_account(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # Deletes the user's rows from every table that has a user_id column
    for table in Base.metadata.sorted_tables:
        if "user_id" in table.c:
            db.execute(table.delete().where(table.c.user_id == user.id))
    db.delete(user)
    db.commit()
    return {"deleted": True}