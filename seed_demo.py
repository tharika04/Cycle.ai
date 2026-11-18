"""Seed a safe, realistic six-month HerRhythm demo account.

Run from the project root:
    python seed_demo.py

The script only writes to the dedicated demo account and is safe to rerun.
It never deletes or updates user-created rows.
"""

import random
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, inspect, text

from backend import day_models, models
from backend.auth import hash_password
from backend.database import Base, SessionLocal, engine
from backend.daylog_model import DayTag


DEMO_EMAIL = "demo@herrhythm.local"
DEMO_PASSWORD = "demo1234"
SEED_KEY = "herrhythm-demo-six-months-v1"

# Six gaps produce seven periods covering more than six months.
CYCLE_LENGTHS = [29, 31, 28, 32, 30, 29]
PERIOD_LENGTHS = [5, 4, 5, 6, 4, 5, 5]
FLOW_LEVELS = ["medium", "heavy", "light", "medium", "medium", "light", "medium"]
MOODS = ["happy", "calm", "tired", "anxious", "irritable", "sad"]
SYMPTOM_TAGS = {
    "cramps": ("Cramps", 2, 4),
    "fatigue": ("Fatigue", 2, 3),
    "headache": ("Headache", 1, 3),
    "bloating": ("Bloating", 1, 3),
    "breast tenderness": ("Tender breasts", 1, 3),
    "cravings": ("Cravings", 1, 3),
    "mood swings": ("Mood swings", 2, 3),
    "acne": ("Acne", 1, 2),
    "insomnia": ("Insomnia", 1, 2),
}


def ensure_seed_tables():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS synthetic_seed_runs ("
            "seed_key VARCHAR(120) PRIMARY KEY, user_id INTEGER NOT NULL, "
            "anchor_date DATE NOT NULL, created_at DATETIME NOT NULL)"
        ))
        daily_columns = {column["name"] for column in inspect(engine).get_columns("daily_logs")}
        if "stress" not in daily_columns:
            conn.execute(text("ALTER TABLE daily_logs ADD COLUMN stress INTEGER"))


def get_demo_user(db):
    user = db.query(models.User).filter(
        func.lower(models.User.email) == DEMO_EMAIL
    ).first()
    if user is None:
        user = models.User(
            name="HerRhythm Demo",
            age=28,
            email=DEMO_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
        )
        db.add(user)
        db.flush()
    return user


def get_anchor(db, user_id):
    row = db.execute(
        text("SELECT anchor_date FROM synthetic_seed_runs WHERE seed_key = :key"),
        {"key": SEED_KEY},
    ).first()
    if row:
        value = row[0]
        return value if isinstance(value, date) else date.fromisoformat(value)

    anchor = date.today() - timedelta(days=12)
    db.execute(
        text(
            "INSERT INTO synthetic_seed_runs "
            "(seed_key, user_id, anchor_date, created_at) "
            "VALUES (:key, :user_id, :anchor, :created)"
        ),
        {
            "key": SEED_KEY,
            "user_id": user_id,
            "anchor": anchor,
            "created": datetime.now(timezone.utc),
        },
    )
    return anchor


def build_cycles(anchor):
    starts = [anchor]
    for gap in reversed(CYCLE_LENGTHS):
        starts.append(starts[-1] - timedelta(days=gap))
    starts.reverse()
    return [
        {
            "start": start,
            "end": start + timedelta(days=PERIOD_LENGTHS[i] - 1),
            "flow": FLOW_LEVELS[i],
            "length": CYCLE_LENGTHS[i] if i < len(CYCLE_LENGTHS) else 30,
        }
        for i, start in enumerate(starts)
    ]


def phase_for(day_in_cycle, period_length, cycle_length):
    if day_in_cycle <= period_length:
        return "menstrual"
    ovulation_day = cycle_length - 14
    if day_in_cycle < ovulation_day - 1:
        return "follicular"
    if day_in_cycle <= ovulation_day + 1:
        return "ovulation"
    if day_in_cycle >= cycle_length - 4:
        return "premenstrual"
    return "luteal"


def daily_values(phase, rng):
    energy_base = {
        "menstrual": 2.5,
        "follicular": 3.8,
        "ovulation": 4.5,
        "luteal": 3.3,
        "premenstrual": 2.8,
    }[phase]
    stress_base = {
        "menstrual": 3.2,
        "follicular": 2.1,
        "ovulation": 1.8,
        "luteal": 2.7,
        "premenstrual": 3.6,
    }[phase]
    sleep = 7.3 if phase in ("follicular", "ovulation") else 6.8
    return {
        "water_glasses": rng.randint(6, 10),
        "sleep_hours": round(max(5.5, sleep + rng.uniform(-0.8, 0.8)) * 2) / 2,
        "exercise_minutes": rng.choice([0, 15, 20, 30, 40, 50]),
        "energy": max(1, min(5, round(energy_base + rng.uniform(-0.7, 0.7)))),
        "stress": max(1, min(5, round(stress_base + rng.uniform(-0.7, 0.7)))),
        "mood": rng.choice(MOODS),
    }


def symptoms_for(phase, day_in_cycle, rng):
    candidates = []
    if phase == "menstrual":
        candidates.extend(["cramps", "fatigue"])
        if day_in_cycle <= 2:
            candidates.append("headache")
    elif phase == "premenstrual":
        candidates.extend(["bloating", "mood swings", "breast tenderness", "cravings"])
        if day_in_cycle % 2 == 0:
            candidates.append("acne")
    elif phase == "ovulation":
        candidates.append("bloating")
    elif day_in_cycle % 9 == 0:
        candidates.append("headache")

    if candidates and rng.random() < 0.72:
        selected = [candidates[0]]
        if len(candidates) > 1 and rng.random() < 0.35:
            selected.append(rng.choice(candidates[1:]))
        return [
            (name, rng.randint(SYMPTOM_TAGS[name][1], SYMPTOM_TAGS[name][2]))
            for name in selected
        ]
    return []


def find_cycle(cycles, day):
    index = max(i for i, cycle in enumerate(cycles) if cycle["start"] <= day)
    cycle = cycles[index]
    return cycle, (day - cycle["start"]).days + 1


def main():
    ensure_seed_tables()
    db = SessionLocal()
    inserted = {"cycles": 0, "daily_logs": 0, "symptoms": 0, "day_tags": 0}
    try:
        user = get_demo_user(db)
        anchor = get_anchor(db, user.id)
        cycles = build_cycles(anchor)

        for cycle in cycles:
            existing = db.query(models.Cycle).filter_by(
                user_id=user.id, start_date=cycle["start"]
            ).first()
            if existing is None:
                db.add(models.Cycle(
                    user_id=user.id,
                    start_date=cycle["start"],
                    end_date=cycle["end"],
                    flow_level=cycle["flow"],
                ))
                inserted["cycles"] += 1

        today = date.today()
        day = cycles[0]["start"]
        while day <= today:
            cycle, day_in_cycle = find_cycle(cycles, day)
            phase = phase_for(day_in_cycle, (cycle["end"] - cycle["start"]).days + 1, cycle["length"])
            day_rng = random.Random(20261108 + day.toordinal())

            if db.query(models.DailyLog).filter_by(user_id=user.id, date=day).first() is None:
                values = daily_values(phase, day_rng)
                db.add(models.DailyLog(user_id=user.id, date=day, **values))
                inserted["daily_logs"] += 1

            for symptom, severity in symptoms_for(phase, day_in_cycle, day_rng):
                row = db.query(models.Symptom).filter_by(
                    user_id=user.id, date=day, symptom=symptom
                ).first()
                if row is None:
                    mood = "tired" if symptom == "fatigue" else (
                        "irritable" if symptom == "mood swings" else None
                    )
                    db.add(models.Symptom(
                        user_id=user.id, date=day, symptom=symptom,
                        severity=severity, mood=mood,
                    ))
                    inserted["symptoms"] += 1

                tag = SYMPTOM_TAGS[symptom][0]
                if db.query(DayTag).filter_by(
                    user_id=user.id, date=day, category="symptoms", tag=tag
                ).first() is None:
                    db.add(DayTag(
                        user_id=user.id, date=day, category="symptoms", tag=tag
                    ))
                    inserted["day_tags"] += 1

            # Add the phase-appropriate discharge marker for calendar detail views.
            if phase == "ovulation":
                tag = "Egg white"
            elif phase in ("menstrual", "premenstrual"):
                tag = "Spotting" if phase == "premenstrual" else "No discharge"
            else:
                tag = "Creamy"
            if db.query(DayTag).filter_by(
                user_id=user.id, date=day, category="discharge", tag=tag
            ).first() is None:
                db.add(DayTag(
                    user_id=user.id, date=day, category="discharge", tag=tag
                ))
                inserted["day_tags"] += 1
            day += timedelta(days=1)

        db.commit()
        last_cycle = cycles[-1]
        ovulation = last_cycle["start"] + timedelta(days=last_cycle["length"] - 14)
        fertile_start = ovulation - timedelta(days=5)
        fertile_end = ovulation + timedelta(days=1)
        print("Seed complete.")
        print("Demo login: " + DEMO_EMAIL + " / " + DEMO_PASSWORD)
        print("Demo user id: " + str(user.id))
        print("Cycle starts: " + str(len(cycles)) + " (" + cycles[0]["start"].isoformat() +
              " through " + cycles[-1]["start"].isoformat() + ")")
        print("Estimated latest ovulation: " + ovulation.isoformat())
        print("Latest fertile window: " + fertile_start.isoformat() + " through " + fertile_end.isoformat())
        for name, count in inserted.items():
            print("Inserted " + name + ": " + str(count))
        print("Rerunning this command will insert zero duplicates.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
