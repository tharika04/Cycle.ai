import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "")
THINKING = os.getenv("GEMINI_THINKING", "minimal").lower()

SYSTEM_PROMPT = """You are HerBot, the friendly assistant inside HerRhythm, a menstrual and reproductive health tracker.
If asked your name, say you are HerBot.
Rules:
- Be warm, clear, and brief (under 120 words unless asked for more).
- Give general educational information only. Never diagnose, and never prescribe medicines or doses.
- Use the user's cycle context below when it is relevant, and mention it naturally.
- Do not promise that predictions are accurate or reliable for contraception.
- For pain, bleeding, or symptoms that sound worrying, suggest seeing a doctor.
- If a question is unrelated to menstrual, reproductive, or general wellbeing, politely redirect.
- Write the whole reply in ONE language and ONE script. Never mix languages or scripts.
- Reply in the language given below. If none is given, use the language the user writes in."""

MEDICAL_FLAGS = [
    "soaking through", "soaked through", "soak a pad", "soaking a pad", "very heavy bleeding",
    "bleeding a lot", "heavy bleeding", "faint", "passed out", "severe pain", "unbearable pain",
    "worst pain", "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "bleeding and pregnant", "pregnant and bleeding", "clots bigger",
]
CRISIS_FLAGS = ["suicid", "kill myself", "end my life", "want to die", "self harm", "self-harm", "hurt myself"]

MEDICAL_WARNING = (
    "**This could need urgent medical attention.** Please contact a doctor or go to the nearest "
    "hospital soon, especially if the symptoms are severe or getting worse. "
    "In an emergency, call your local emergency number (112 in India)."
)
CRISIS_MESSAGE = (
    "I'm really sorry you're feeling this way. You deserve support right now. "
    "Please reach out to someone you trust, or contact your local emergency number "
    "(112 in India) or a mental health helpline in your area. You don't have to handle this alone."
)


def find_flag(text):
    t = text.lower()
    if any(f in t for f in CRISIS_FLAGS):
        return "crisis"
    if any(f in t for f in MEDICAL_FLAGS):
        return "medical"
    return None


def build_context(prediction, symptoms):
    lines = ["User's cycle context:"]
    if prediction.get("status") == "ok":
        lines.append("- Current phase: " + prediction["current_phase"])
        lines.append("- Day of cycle: " + str(prediction["day_in_cycle"]))
        lines.append("- Days until next period: " + str(prediction["days_until_next_period"]))
        lines.append("- Average cycle length: " + str(prediction["avg_cycle_length"]) + " days")
        lines.append("- Cycles logged: " + str(prediction["cycles_logged"]))
        if prediction.get("irregular"):
            lines.append("- Cycles look irregular")
    else:
        lines.append("- No cycle data logged yet")
    if symptoms:
        recent = ", ".join(
            s.symptom + " (" + str(s.severity) + "/5, " + s.date.isoformat() + ")" for s in symptoms
        )
        lines.append("- Recent symptoms: " + recent)
    else:
        lines.append("- No symptoms logged recently")
    return "\n".join(lines)


def _is_busy(error):
    text = str(error)
    return any(k in text for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))


def _is_missing(error):
    text = str(error)
    return "404" in text or "NOT_FOUND" in text


def _config(system_text, level):
    kwargs = {"system_instruction": system_text, "temperature": 0.5}
    if level:
        kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=level)
    return types.GenerateContentConfig(**kwargs)


def _levels():
    if THINKING in ("off", "none", ""):
        return [None]
    order = [THINKING, "low", None]
    seen = []
    for x in order:
        if x not in seen:
            seen.append(x)
    return seen


def generate_reply(message, history, context):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the project root .env file "
            "(not .env.example), then restart the backend."
        )

    client = genai.Client(api_key=api_key)

    contents = []
    for h in history:
        contents.append(types.Content(role="user", parts=[types.Part(text=h.message)]))
        contents.append(types.Content(role="model", parts=[types.Part(text=h.response)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    system_text = SYSTEM_PROMPT + "\n\n" + context

    models = [MODEL]
    if FALLBACK_MODEL and FALLBACK_MODEL != MODEL:
        models.append(FALLBACK_MODEL)

    last_error = None
    for model in models:
        levels = _levels()
        idx = 0
        busy_tries = 0
        while busy_tries < 2:
            level = levels[idx]
            started = time.time()
            try:
                response = client.models.generate_content(
                    model=model, contents=contents, config=_config(system_text, level)
                )
                print("[chat] model=" + model + " thinking=" + str(level)
                      + " took " + str(round(time.time() - started, 1)) + "s", flush=True)
                text = (response.text or "").strip()
                return text or "Sorry, I couldn't come up with an answer. Please try rephrasing."
            except Exception as e:
                last_error = e
                print("[chat] model=" + model + " thinking=" + str(level)
                      + " failed after " + str(round(time.time() - started, 1)) + "s: "
                      + str(e)[:120], flush=True)
                if level and "thinking" in str(e).lower() and idx + 1 < len(levels):
                    idx += 1
                    continue
                if _is_missing(e):
                    break
                if not _is_busy(e):
                    raise
                busy_tries += 1
                time.sleep(1)
    raise last_error