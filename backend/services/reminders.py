import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from backend.services.predictor import predict

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PHASE_TIPS = {
    "menstrual": "Rest, stay warm and hydrated, and eat iron-rich foods.",
    "follicular": "Energy is rising. A good time to train harder or start something new.",
    "ovulation": "Many people feel most energetic around now.",
    "luteal": "PMS may show up. Plan lighter days and protect your sleep.",
}
WATER_TARGET = 8


def _item(kind, title, message):
    return {"kind": kind, "title": title, "message": message}


def build_reminders(cycles, daily_logs, today=None):
    today = today or date.today()
    pred = predict(cycles, today)
    if pred.get("status") != "ok":
        return [_item("log", "Log your first period",
                      "Add your last period on the Log Data page to get predictions and reminders.")]

    items = []
    left = pred["days_until_next_period"]
    if left < 0:
        late = -left
        msg = "Your period is about " + str(late) + " day(s) later than predicted. Log it when it starts."
        if late >= 7:
            msg += " If you could be pregnant, consider a test, and see a doctor if it stays away."
        items.append(_item("late", "Period is late", msg))
    elif left == 0:
        items.append(_item("period", "Your period is expected today", "Keep supplies with you."))
    elif left <= 3:
        items.append(_item("period", "Period expected in " + str(left) + " day(s)",
                           "Keep supplies ready. Light exercise and warm drinks can help with PMS."))

    fw = pred["fertile_window"]
    if fw["start"] <= today <= fw["end"]:
        items.append(_item("fertile", "You are in your estimated fertile window",
                           "It ends on " + fw["end"].isoformat() + ". This is an estimate, "
                           "so do not rely on it for contraception."))
    elif 0 < (fw["start"] - today).days <= 2:
        items.append(_item("fertile", "Fertile window starts in " + str((fw["start"] - today).days) + " day(s)",
                           "This is an estimate, so do not rely on it for contraception."))

    if pred["ovulation_date"] == today:
        items.append(_item("fertile", "Estimated ovulation day", "Based on your average cycle length."))

    todays = [l for l in daily_logs if l.date == today]
    if not todays:
        items.append(_item("log", "Log today's check-in", "Tap today's date on the Calendar to log how you feel."))
    else:
        water = todays[0].water_glasses
        if water is not None and water < WATER_TARGET:
            items.append(_item("log", "Drink some water",
                               "You have logged " + str(water) + " glass(es) today. A common target is about "
                               + str(WATER_TARGET) + "."))

    phase = "luteal" if pred["current_phase"] == "late" else pred["current_phase"]
    items.append(_item("tip", "Phase tip: " + phase.title(), PHASE_TIPS[phase]))
    return items


def reminders_to_text(items, name):
    lines = ["Hi " + name + ",", "", "Here are your HerRhythm reminders for " + date.today().isoformat() + ":", ""]
    for it in items:
        lines.append("- " + it["title"] + ": " + it["message"])
    lines += ["", "These are estimates based on your logs, not medical advice.", "HerRhythm"]
    return "\n".join(lines)


def send_email(to_addr, subject, body):
    host = os.getenv("SMTP_HOST")
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as exc:
        raise RuntimeError("SMTP_PORT must be a number, usually 587.") from exc
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
    if not (host and user and password):
        raise RuntimeError(
            "Email is not set up yet. Add SMTP_HOST, SMTP_PORT, SMTP_USER, "
            "SMTP_PASSWORD, and SMTP_FROM to the project root .env, then restart the backend."
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_FROM", user)
    msg["To"] = to_addr
    msg.set_content(body)

    try:
        smtp_class = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
        with smtp_class(host, port, timeout=20) as server:
            if port != 465:
                server.starttls()
            server.login(user, password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            "SMTP authentication failed. For Gmail, use a 16-character Google "
            "App Password with 2-Step Verification enabled."
        ) from exc
    except (OSError, smtplib.SMTPException) as exc:
        raise RuntimeError(
            "SMTP connection failed for " + host + ":" + str(port) +
            ". Check the SMTP host/port and network connection."
        ) from exc