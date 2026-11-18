import calendar
import math
from datetime import date, timedelta

import api_client as api

STYLE = {
    "pl": ("#ff4d79", "#ffffff"),
    "pp": ("#ffc2d1", "#a3194a"),
    "ov": ("#f4c542", "#5a4300"),
    "fw": ("#8fdcb4", "#0b4a2a"),
}


def build_marks(cycles, pred, today):
    P = int(pred["avg_period_length"])
    L = int(pred["avg_cycle_length"])
    ordered = sorted(cycles, key=lambda c: c["start_date"])
    next_original = date.fromisoformat(pred["next_period_start"])
    logged, predicted, fertile, ovulation = set(), set(), set(), set()

    def add_fertile(ov):
        ovulation.add(ov)
        for k in range(-5, 2):
            fertile.add(ov + timedelta(days=k))

    for i, c in enumerate(ordered):
        start = date.fromisoformat(c["start_date"])
        if c["end_date"]:
            end = date.fromisoformat(c["end_date"])
        else:
            end = min(start + timedelta(days=P - 1), today)
        end = max(end, start)
        d = start
        while d <= end:
            logged.add(d)
            d += timedelta(days=1)

        if i + 1 < len(ordered):
            nxt = date.fromisoformat(ordered[i + 1]["start_date"])
            if not 15 <= (nxt - start).days <= 60:
                nxt = start + timedelta(days=L)
        else:
            nxt = next_original
        add_fertile(nxt - timedelta(days=14))

    base = max(next_original, today)
    horizon = date(today.year + 1, 12, 31)
    k = 0
    while True:
        start = base + timedelta(days=k * L)
        if start > horizon:
            break
        for j in range(P):
            predicted.add(start + timedelta(days=j))
        if k >= 1:
            add_fertile(start - timedelta(days=14))
        k += 1
    return {"logged": logged, "predicted": predicted, "fertile": fertile, "ovulation": ovulation}


def day_class(d, marks):
    if d in marks["logged"]:
        return "pl"
    if d in marks["predicted"]:
        return "pp"
    if d in marks["ovulation"]:
        return "ov"
    if d in marks["fertile"]:
        return "fw"
    return ""


def month_wheel_svg(pred, marks, today):
    """Ring of this month's dates, coloured exactly like the calendar."""
    n = calendar.monthrange(today.year, today.month)[1]
    cx = cy = 200
    R, r = 158, 12

    if pred:
        left = int(pred["days_until_next_period"])
        if left > 0:
            line4 = "Period in %d days" % left
        elif left == 0:
            line4 = "Period expected today"
        else:
            line4 = "%d days late" % (-left)
        line2 = "Day %d" % int(pred["day_in_cycle"])
        line3 = pred["current_phase"].title()
    else:
        line2, line3, line4 = "Welcome", "Add your last period", "Tap Track below"
    line1 = "%d %s" % (today.day, calendar.month_abbr[today.month])

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">']
    p.append(
        '<defs><radialGradient id="g" cx="50%" cy="35%" r="75%">'
        '<stop offset="0%" stop-color="#ff8fb0"/><stop offset="100%" stop-color="#f0457a"/>'
        "</radialGradient></defs>"
    )
    p.append('<circle cx="200" cy="200" r="190" fill="#f1ecee"/>')
    p.append('<circle cx="200" cy="200" r="130" fill="#ffffff"/>')

    def pos(day):
        a = math.radians(-90 + (day - 1) * 360 / n)
        return cx + R * math.cos(a), cy + R * math.sin(a)

    for day in range(1, n + 1):
        d = date(today.year, today.month, day)
        cls = day_class(d, marks) if pred else ""
        fill, txt = STYLE.get(cls, ("#ffffff", "#9a8f94"))
        x, y = pos(day)
        p.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (x, y, r, fill))
        p.append(
            '<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" fill="%s" '
            'font-family="Arial, sans-serif">%d</text>' % (x, y + 4, txt, day)
        )
    x, y = pos(today.day)
    p.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="none" stroke="#2b2b2b" stroke-width="3"/>' % (x, y, r + 5))

    p.append('<circle cx="200" cy="200" r="108" fill="url(#g)"/>')
    p.append('<text x="200" y="158" font-size="15" text-anchor="middle" fill="#ffe6ee" font-family="Arial, sans-serif">%s</text>' % line1)
    p.append('<text x="200" y="198" font-size="34" font-weight="700" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif">%s</text>' % line2)
    p.append('<text x="200" y="226" font-size="17" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif">%s</text>' % line3)
    p.append('<text x="200" y="250" font-size="14" text-anchor="middle" fill="#ffe6ee" font-family="Arial, sans-serif">%s</text>' % line4)
    p.append("</svg>")
    return "".join(p)


def wheel_for_home(pred):
    today = date.today()
    if not pred:
        return month_wheel_svg(None, {"logged": set(), "predicted": set(), "fertile": set(), "ovulation": set()}, today)
    marks = build_marks(api.get_cycles(), pred, today)
    return month_wheel_svg(pred, marks, today)


def show_wheel(pred):
    """Date wheel for Home, with its colour legend underneath."""
    import streamlit as st

    st.image(wheel_for_home(pred), width=340)
    st.markdown(
        "<div class='legend'><span style='background:#ff4d79'></span>Period"
        "<span style='background:#ffc2d1'></span>Predicted period"
        "<span style='background:#8fdcb4'></span>Fertile window"
        "<span style='background:#f4c542'></span>Ovulation</div>",
        unsafe_allow_html=True,
    )