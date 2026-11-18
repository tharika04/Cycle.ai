from datetime import date, timedelta

from backend.services.predictor import detect_phase, predict

BASELINE = {
    "menstrual": {"energy": 2.5, "mood": 3.0},
    "follicular": {"energy": 3.8, "mood": 4.0},
    "ovulation": {"energy": 4.4, "mood": 4.2},
    "luteal": {"energy": 3.2, "mood": 3.3},
}
MOOD_SCORE = {"happy": 5, "calm": 4, "tired": 3, "anxious": 2, "irritable": 2, "sad": 1}
TIPS = {
    "menstrual": "Go gentle: rest, warmth, and iron-rich food.",
    "follicular": "Energy is rising. A good time to start something new or train harder.",
    "ovulation": "Many people feel most energetic and social around now.",
    "luteal": "Energy may dip. Plan lighter days, eat steadily, and protect your sleep.",
}
SAMPLE_WEIGHT = 3


def mood_label(score):
    if score >= 4:
        return "Upbeat"
    if score >= 3:
        return "Steady"
    if score >= 2:
        return "Sensitive"
    return "Low"


def _phase(day, period_len, cycle_len):
    phase = detect_phase(day, period_len, cycle_len - 14, cycle_len)
    return "luteal" if phase == "late" else phase


def _personal_stats(logs, starts, period_len, cycle_len):
    stats = {p: {"energy": [], "mood": []} for p in BASELINE}
    for log in logs:
        earlier = [s for s in starts if s <= log.date]
        if not earlier:
            continue
        day = (log.date - earlier[-1]).days + 1
        if day > cycle_len + 7:
            continue
        phase = _phase(day, period_len, cycle_len)
        if log.energy is not None:
            stats[phase]["energy"].append(log.energy)
        if log.mood in MOOD_SCORE:
            stats[phase]["mood"].append(MOOD_SCORE[log.mood])
    return stats


def _blend(baseline, values):
    if not values:
        return baseline
    weight = len(values) / (len(values) + SAMPLE_WEIGHT)
    return weight * (sum(values) / len(values)) + (1 - weight) * baseline


def _clamp(x):
    return round(min(5.0, max(1.0, x)), 1)


def build_forecast(cycles, logs, today=None, days=7):
    today = today or date.today()
    pred = predict(cycles, today)
    if pred.get("status") != "ok":
        return {"status": "no_data", "message": "Log your first period to get a forecast."}

    cycle_len = pred["avg_cycle_length"]
    period_len = pred["avg_period_length"]
    last_start = pred["last_period_start"]
    starts = sorted(c.start_date for c in cycles)
    stats = _personal_stats(logs, starts, period_len, cycle_len)
    late = pred["day_in_cycle"] > cycle_len

    out = []
    for i in range(days):
        d = today + timedelta(days=i)
        raw_day = (d - last_start).days + 1
        if raw_day > cycle_len:
            day = cycle_len if late else ((raw_day - 1) % cycle_len) + 1
        else:
            day = max(raw_day, 1)

        phase = _phase(day, period_len, cycle_len)
        base_energy = BASELINE[phase]["energy"]
        base_mood = BASELINE[phase]["mood"]
        if phase == "luteal" and cycle_len - day <= 4:
            base_energy -= 0.4
            base_mood -= 0.4

        energy = _clamp(_blend(base_energy, stats[phase]["energy"]))
        mood = _clamp(_blend(base_mood, stats[phase]["mood"]))
        out.append({
            "date": d.isoformat(),
            "day_in_cycle": day,
            "phase": phase,
            "energy": energy,
            "mood": mood,
            "mood_label": mood_label(mood),
            "tip": TIPS[phase],
            "personalized": bool(stats[phase]["energy"] or stats[phase]["mood"]),
        })

    entries = len([l for l in logs if l.energy is not None or l.mood in MOOD_SCORE])
    return {"status": "ok", "personalized_entries": entries, "days": out}