import os
import json
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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
RESEND_API_URL = "https://api.resend.com/emails"


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
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()
    if not api_key or not from_email:
        raise EmailConfigurationError(
            "Email reminders aren't configured. Set RESEND_API_KEY and "
            "RESEND_FROM_EMAIL, then restart the backend."
        )

    payload = json.dumps({
        "from": from_email,
        "to": [to_addr],
        "subject": subject,
        "text": body,
    }).encode("utf-8")
    request = Request(
        RESEND_API_URL,
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20):
            pass
    except HTTPError as exc:
        if exc.code == 401:
            message = "Email service authentication failed. Check RESEND_API_KEY."
        elif exc.code in (400, 403, 422):
            message = (
                "Resend rejected the configured sender. Verify the sender/domain "
                "in Resend and check RESEND_FROM_EMAIL."
            )
        elif exc.code == 429:
            message = "The email service is temporarily rate-limited. Please try again later."
        else:
            message = "The email service couldn't send your reminder. Please try again later."
        raise EmailDeliveryError(message) from None
    except (URLError, TimeoutError, OSError):
        raise EmailDeliveryError(
            "The email service couldn't be reached. Please try again later."
        ) from None


class EmailConfigurationError(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    pass