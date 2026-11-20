import json
import logging
import os
import re
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
logger = logging.getLogger(__name__)
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_BEARER_RE = re.compile(r"(?i)\bBearer\s+\S+")
_API_KEY_RE = re.compile(r"\bre_[A-Za-z0-9_-]+\b")
_HEALTH_CONTENT_RE = re.compile(
    r"(?i)\b(?:health|symptom|cycle|period|menstrual|pregnan(?:t|cy)|"
    r"ovulation|fertile|cramp|bleed(?:ing)?|pain|medication|diagnos(?:is|ed))\b"
)


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


def _resend_error_info(error, api_key):
    try:
        raw_body = error.read(8192).decode("utf-8", errors="replace")
        response = json.loads(raw_body)
    except (OSError, ValueError):
        raw_body = ""
        response = {}
    if not isinstance(response, dict):
        response = {}

    safe_body = {}
    for key in ("statusCode", "name", "code", "message"):
        value = response.get(key)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            if isinstance(value, str):
                if _HEALTH_CONTENT_RE.search(value):
                    value = "[redacted sensitive content]"
                else:
                    value = _EMAIL_RE.sub("[redacted email]", value)
                    value = _BEARER_RE.sub("Bearer [redacted]", value)
                    value = _API_KEY_RE.sub("[redacted API key]", value)
                    if api_key:
                        value = value.replace(api_key, "[redacted API key]")
            safe_body[key] = value
    safe_keys = {"statusCode", "name", "code", "message"}
    raw_body_is_safe = (
        raw_body
        and set(response).issubset(safe_keys)
        and not _EMAIL_RE.search(raw_body)
        and not _BEARER_RE.search(raw_body)
        and not _API_KEY_RE.search(raw_body)
        and not _HEALTH_CONTENT_RE.search(raw_body)
        and (not api_key or api_key not in raw_body)
    )
    response_body = (
        raw_body if raw_body_is_safe else
        json.dumps(safe_body, separators=(",", ":"), ensure_ascii=True)
    )
    if not safe_body and raw_body:
        response_body = "[redacted unrecognized response body]"

    error_type = response.get("name") or response.get("code") or "unspecified"
    safe_error_types = {
        "application_error",
        "invalid_api_key",
        "internal_server_error",
        "missing_api_key",
        "rate_limit_exceeded",
        "restricted_api_key",
        "validation_error",
    }
    if not isinstance(error_type, str) or error_type not in safe_error_types:
        error_type = "unspecified"

    provider_message = response.get("message", "")
    if not isinstance(provider_message, str):
        provider_message = ""
    provider_message = provider_message.lower()

    if (
        "testing emails" in provider_message
        and ("own email" in provider_message or "only send" in provider_message)
    ):
        category = "test_recipient_restriction"
    elif error.code == 401:
        category = "authentication"
    elif error.code == 429:
        category = "rate_limited"
    elif error.code in (400, 403, 422):
        category = "sender_or_request_rejected"
    else:
        category = "provider_failure"

    return error_type, category, response_body


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
        with urlopen(request, timeout=20) as response:
            logger.info("Resend email API request accepted: status=%s", response.status)
    except HTTPError as exc:
        error_type, category, response_body = _resend_error_info(exc, api_key)
        logger.warning(
            "Resend email API rejected request: status=%d error_type=%s "
            "category=%s response_body=%s",
            exc.code,
            error_type,
            category,
            response_body,
        )
        if category == "test_recipient_restriction":
            message = (
                "Resend's onboarding sender can only send test emails to the email "
                "address on your Resend account. To email other users, verify a "
                "domain in Resend and set RESEND_FROM_EMAIL to an address on it."
            )
        elif category == "authentication":
            message = "Email service authentication failed. Check RESEND_API_KEY."
        elif category == "sender_or_request_rejected":
            message = (
                "Resend rejected the email request. Check that RESEND_FROM_EMAIL "
                "uses a verified sender and try again."
            )
        elif category == "rate_limited":
            message = "The email service is temporarily rate-limited. Please try again later."
        else:
            message = "The email service couldn't send your reminder. Please try again later."
        raise EmailDeliveryError(message) from None
    except (URLError, TimeoutError, OSError) as exc:
        logger.warning(
            "Resend email API request failed before an HTTP response: error_type=%s",
            type(exc).__name__,
        )
        raise EmailDeliveryError(
            "The email service couldn't be reached. Please try again later."
        ) from None


class EmailConfigurationError(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    pass