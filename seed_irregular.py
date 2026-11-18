"""Fills a HerRhythm account with about 6 months of demo data for a person
with irregular cycles. Meant for testing the Health Check page.

Run from the cycle-ai folder with the venv active:
    python seed_irregular.py your-email@example.com
"""
import random
import sys
from datetime import date, timedelta

from sqlalchemy import func

from backend import models
from backend.database import Base, SessionLocal, engine

random.seed(11)

GAPS = [19, 36, 27, 42, 24]            # days between period starts (oldest first)
DURATIONS = [5, 4, 6, 8, 9, 8]         # period length in days (6 periods)
FLOWS = ["medium", "light", "medium", "heavy", "heavy", "heavy"]
DAYS_SINCE_LAST_START = 38             # the next period is late
CURRENT_CYCLE_GUESS = 30

ENERGY = {"menstrual": 2.2, "follicular": 3.4, "ovulation": 3.8,
          "luteal": 3.0, "premenstrual": 2.4, "late": 2.6}
MOOD_CHOICES = {
    "menstrual": ["tired", "sad", "tired", "calm"],
    "follicular": ["calm", "happy", "calm", "tired"],
    "ovulation": ["happy", "calm", "happy"],
    "luteal": ["calm", "anxious", "tired"],
    "premenstrual": ["irritable", "anxious", "sad", "tired"],
    "late": ["anxious", "irritable", "tired"],
}
EXERCISE = {
    "menstrual": [0, 0, 0, 15, 20],
    "follicular": [0, 20, 30, 45, 0],
    "ovulation": [0, 30, 45, 20],
    "luteal": [0, 0, 20, 30],
    "premenstrual": [0, 0, 0, 15],
    "late": [0, 0, 15, 20],
}


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def maybe(prob):
    return random.random() < prob


def build_starts(today):
    starts = [today - timedelta(days=DAYS_SINCE_LAST_START)]
    for gap in reversed(GAPS):
        starts.append(starts[-1] - timedelta(days=gap))
    starts.reverse()
    return starts


def day_info(d, starts):
    idx = max(i for i, s in enumerate(starts) if s <= d)
    day = (d - starts[idx]).days + 1
    length = CURRENT_CYCLE_GUESS if idx >= len(GAPS) else GAPS[idx]
    if day <= DURATIONS[idx]:
        phase = "menstrual"
    elif day > length:
        phase = "late"
    elif day < length - 15:
        phase = "follicular"
    elif day <= length - 13:
        phase = "ovulation"
    elif day >= length - 4:
        phase = "premenstrual"
    else:
        phase = "luteal"
    return day, phase


def symptoms_for(day, phase):
    rows = []

    def add(name, severity, mood=None):
        rows.append((name, severity, mood))

    if phase == "menstrual":
        if day == 1:
            if maybe(0.95):
                sev = random.choice([3, 4, 5])
                add("cramps", sev, "tired")
                if sev >= 4 and maybe(0.6):
                    add("pain - lower abdomen", sev)
            if maybe(0.8):
                add("fatigue", 3, "tired")
            if maybe(0.6):
                add("back pain", random.choice([3, 4]))
            if maybe(0.4):
                add("headache", 3)
        elif day == 2:
            if maybe(0.85):
                sev = random.choice([3, 4, 4])
                add("cramps", sev, "tired")
                if sev >= 4 and maybe(0.5):
                    add("pain - lower abdomen", sev)
            if maybe(0.7):
                add("fatigue", 3, "tired")
            if maybe(0.4):
                add("back pain", 3)
        elif day == 3:
            if maybe(0.6):
                add("cramps", random.choice([2, 3]))
            if maybe(0.4):
                add("bloating", 2)
        else:
            if maybe(0.4):
                add("fatigue", random.choice([2, 3]), "tired")
            if maybe(0.3):
                add("cramps", 2)
    elif phase == "premenstrual":
        if maybe(0.7):
            add("bloating", random.choice([2, 3, 3]))
        if maybe(0.65):
            add("mood swings", random.choice([3, 3, 4]), random.choice(["irritable", "anxious", "sad"]))
        if maybe(0.5):
            add("breast tenderness", random.choice([2, 3]))
        if maybe(0.55):
            add("cravings", random.choice([2, 3]))
        if maybe(0.4):
            add("acne", random.choice([2, 3]))
        if maybe(0.35):
            add("headache", random.choice([2, 3]))
        if maybe(0.4):
            add("insomnia", 3, "tired")
        if maybe(0.4):
            add("fatigue", 3, "tired")
    elif phase == "late":
        if maybe(0.35):
            add("mood swings", 3, random.choice(["anxious", "irritable"]))
        if maybe(0.3):
            add("bloating", 2)
        if maybe(0.4):
            add("fatigue", 3, "tired")
        if maybe(0.25):
            add("headache", 2)
        if maybe(0.3):
            add("insomnia", 3, "anxious")
    elif phase == "luteal":
        if maybe(0.25):
            add("bloating", random.choice([1, 2]))
        if maybe(0.15):
            add("fatigue", 2)

    if phase in ("follicular", "ovulation") and maybe(0.05):
        add("headache", 2)
    return rows


def daily_for(phase):
    energy = int(clamp(round(ENERGY[phase] + random.uniform(-1.0, 1.0)), 1, 5))
    if phase in ("premenstrual", "late"):
        sleep = random.uniform(4.5, 6.5)
    elif phase == "menstrual":
        sleep = random.uniform(5.5, 7.5)
    else:
        sleep = random.uniform(5.5, 8.0)
    sleep = round(sleep * 2) / 2
    water = random.randint(3, 8)
    exercise = random.choice(EXERCISE[phase])
    mood = random.choice(MOOD_CHOICES[phase])
    return water, sleep, exercise, energy, mood


def main():
    if len(sys.argv) < 2:
        print("Usage: python seed_irregular.py your-email@example.com")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = sys.argv[1].strip()
        user = db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()
        if user is None:
            known = [u.email for u in db.query(models.User).all()]
            print("No account found for " + email)
            print("Accounts in the database: " + (", ".join(known) if known else "none"))
            print("Register on the app's Home page first, then run this again.")
            return

        print("This will REPLACE all periods, symptoms, and daily logs for " + user.email + ".")
        if input("Type YES to continue: ").strip().upper() != "YES":
            print("Cancelled. Nothing was changed.")
            return

        has_daily = hasattr(models, "DailyLog")
        db.query(models.Cycle).filter_by(user_id=user.id).delete()
        db.query(models.Symptom).filter_by(user_id=user.id).delete()
        if has_daily:
            db.query(models.DailyLog).filter_by(user_id=user.id).delete()

        today = date.today()
        starts = build_starts(today)

        for i, s in enumerate(starts):
            db.add(models.Cycle(
                user_id=user.id, start_date=s,
                end_date=s + timedelta(days=DURATIONS[i] - 1), flow_level=FLOWS[i],
            ))

        n_symptoms = 0
        n_daily = 0
        d = starts[0]
        while d <= today:
            day, phase = day_info(d, starts)
            for name, severity, mood in symptoms_for(day, phase):
                db.add(models.Symptom(user_id=user.id, date=d, symptom=name, severity=severity, mood=mood))
                n_symptoms += 1
            if has_daily and maybe(0.8):
                water, sleep, exercise, energy, mood = daily_for(phase)
                db.add(models.DailyLog(
                    user_id=user.id, date=d, water_glasses=water, sleep_hours=sleep,
                    exercise_minutes=exercise, energy=energy, mood=mood,
                ))
                n_daily += 1
            d += timedelta(days=1)

        db.commit()
        print("Done for " + user.email + ":")
        print("  periods:     " + str(len(starts)) + " (first start " + starts[0].isoformat() + ")")
        print("  symptoms:    " + str(n_symptoms))
        if has_daily:
            print("  daily logs:  " + str(n_daily))
        else:
            print("  daily logs:  skipped (the Daily Tracker is not set up in this project)")
    finally:
        db.close()


main()