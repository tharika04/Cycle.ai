from datetime import date, timedelta

PAIN_SYMPTOMS = {"cramps", "back pain", "headache"}
LEVEL_RANK = {"ok": 0, "info": 0, "watch": 1, "see_doctor": 2}
DISCLAIMER = (
    "This check uses common general guidelines and only the data you logged. "
    "It is not a diagnosis. Cycles can vary for many reasons, so please talk to a doctor "
    "about anything that worries you."
)


def _finding(level, title, detail):
    return {"level": level, "title": title, "detail": detail}


def screen(cycles, symptoms, today=None):
    today = today or date.today()
    if not cycles:
        return {"status": "no_data", "message": "Log your first period on the Log Data page to run the health check."}

    ordered = sorted(cycles, key=lambda c: c.start_date)
    starts = [c.start_date for c in ordered]
    gaps = [(b - a).days for a, b in zip(starts, starts[1:])]
    lengths = [g for g in gaps if g >= 10][-6:]
    findings = []

    if len(lengths) < 3:
        findings.append(_finding(
            "info", "Not enough data yet",
            "Some checks need at least 3 completed cycles (4 logged period start dates). "
            "Cycles measured so far: " + str(len(lengths)) + ". Log more periods for better results.",
        ))

    if lengths:
        short = [l for l in lengths if l < 21]
        long_ = [l for l in lengths if l > 35]
        if short:
            findings.append(_finding(
                "watch", "Some cycles were shorter than 21 days",
                "Cycle lengths: " + ", ".join(str(x) for x in lengths) + " days. "
                "Very frequent periods are worth mentioning to a doctor if they continue.",
            ))
        if long_:
            findings.append(_finding(
                "watch", "Some cycles were longer than 35 days",
                "Cycle lengths: " + ", ".join(str(x) for x in lengths) + " days. "
                "Infrequent periods have many possible causes, so consider asking a doctor if this continues.",
            ))
        if not short and not long_:
            findings.append(_finding(
                "ok", "Cycle length is in the typical range",
                "Your recent cycles (" + ", ".join(str(x) for x in lengths) + " days) are within 21 to 35 days.",
            ))

    if len(lengths) >= 3:
        spread = max(lengths) - min(lengths)
        if spread > 7:
            findings.append(_finding(
                "watch", "Cycle length varies a lot",
                "Your cycles differ by " + str(spread) + " days (shortest " + str(min(lengths))
                + ", longest " + str(max(lengths)) + "). A difference of more than about 7 days is often "
                "considered irregular. Stress, sleep, weight changes, and health conditions can all play a role.",
            ))
        else:
            findings.append(_finding(
                "ok", "Cycle length is fairly regular",
                "Your cycles differ by " + str(spread) + " days, which is a small variation.",
            ))

    durations = [(c.end_date - c.start_date).days + 1 for c in ordered if c.end_date]
    recent_durations = durations[-6:]
    if recent_durations:
        longest = max(recent_durations)
        if longest > 7:
            findings.append(_finding(
                "watch", "Some periods lasted more than 7 days",
                "Longest recent period: " + str(longest) + " days. Long periods are worth discussing with a doctor.",
            ))
        else:
            findings.append(_finding(
                "ok", "Period length looks typical",
                "Your recent periods lasted up to " + str(longest) + " days.",
            ))

    since = (today - starts[-1]).days
    avg = round(sum(lengths) / len(lengths)) if lengths else 28
    if since > 90:
        findings.append(_finding(
            "see_doctor", "No period logged for " + str(since) + " days",
            "Going more than 3 months without a period is worth discussing with a doctor. "
            "If you had periods you did not log, add them on the Log Data page. "
            "If you could be pregnant, a pregnancy test is a good first step.",
        ))
    elif since > avg + 7:
        late = since - avg
        findings.append(_finding(
            "watch", "Your period is about " + str(late) + " days later than your usual pattern",
            "Stress, illness, travel, and routine changes can delay a period. If you could be pregnant, "
            "consider a test. See a doctor if it stays away or this keeps happening. "
            "If you already had this period, log it on the Log Data page.",
        ))

    last_three = ordered[-3:]
    if len(last_three) == 3 and all(c.flow_level == "heavy" for c in last_three):
        findings.append(_finding(
            "watch", "Heavy flow logged in your last 3 periods",
            "Repeated heavy bleeding can lead to low iron. Please see a doctor if you soak through a pad or "
            "tampon every hour for several hours, pass large clots, or feel dizzy or very tired.",
        ))

    cutoff = today - timedelta(days=90)
    pain_days = {
        s.date for s in symptoms
        if (s.symptom in PAIN_SYMPTOMS or s.symptom.startswith("pain - ")) and s.severity >= 4 and s.date >= cutoff
    }
    if len(pain_days) >= 3:
        findings.append(_finding(
            "watch", "Strong pain logged on " + str(len(pain_days)) + " days in the last 90 days",
            "Pain that is often strong or disrupts daily life should be checked by a doctor.",
        ))

    top = max((LEVEL_RANK[f["level"]] for f in findings), default=0)
    overall = {0: "ok", 1: "watch", 2: "see_doctor"}[top]
    return {
        "status": "ok",
        "overall": overall,
        "cycles_analyzed": len(lengths),
        "findings": findings,
        "disclaimer": DISCLAIMER,
    }