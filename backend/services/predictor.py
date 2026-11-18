from datetime import date, timedelta
from statistics import pstdev

DEFAULT_CYCLE = 28
DEFAULT_PERIOD = 5
LUTEAL = 14


def cycle_lengths(start_dates):
    """Days between consecutive period starts (oldest to newest)."""
    ds = sorted(start_dates)
    return [(b - a).days for a, b in zip(ds, ds[1:]) if 15 <= (b - a).days <= 90]


def weighted_average(values):
    """Recent cycles count more. Uses the last 6."""
    vals = values[-6:]
    weights = range(1, len(vals) + 1)
    return sum(v * w for v, w in zip(vals, weights)) / sum(weights)


def detect_phase(day, period_len, ovulation_day, cycle_len):
    if day > cycle_len + 7:
        return "late"
    if day <= period_len:
        return "menstrual"
    if day < ovulation_day - 1:
        return "follicular"
    if day <= ovulation_day + 1:
        return "ovulation"
    return "luteal"


def predict(cycles, today=None):
    """cycles: list of objects with start_date and end_date."""
    today = today or date.today()
    if not cycles:
        return {"status": "no_data", "message": "Log your first period to get predictions."}

    ordered = sorted(cycles, key=lambda c: c.start_date)
    starts = [c.start_date for c in ordered]
    lengths = cycle_lengths(starts)

    cycle_len = round(weighted_average(lengths)) if lengths else DEFAULT_CYCLE
    period_lens = [(c.end_date - c.start_date).days + 1 for c in ordered if c.end_date]
    period_len = round(sum(period_lens) / len(period_lens)) if period_lens else DEFAULT_PERIOD

    last_start = starts[-1]
    next_period = last_start + timedelta(days=cycle_len)
    ovulation = next_period - timedelta(days=LUTEAL)
    ovulation_day = (ovulation - last_start).days + 1
    day_in_cycle = (today - last_start).days + 1

    n = len(lengths)
    irregular = bool(lengths) and (
        (len(lengths) >= 3 and pstdev(lengths) > 7) or any(l < 21 or l > 35 for l in lengths)
    )

    return {
        "status": "ok",
        "cycles_logged": len(ordered),
        "avg_cycle_length": cycle_len,
        "avg_period_length": period_len,
        "last_period_start": last_start, "last_period_length": ((ordered[-1].end_date - last_start).days + 1) if ordered[-1].end_date else None,
        "next_period_start": next_period,
        "days_until_next_period": (next_period - today).days,
        "ovulation_date": ovulation,
        "fertile_window": {
            "start": ovulation - timedelta(days=5),
            "end": ovulation + timedelta(days=1),
        },
        "day_in_cycle": day_in_cycle,
        "current_phase": detect_phase(day_in_cycle, period_len, ovulation_day, cycle_len),
        "confidence": "low" if n < 3 else "medium" if n < 6 else "high",
        "irregular": irregular,
        "note": "Predictions are estimates, not medical advice.",
    }