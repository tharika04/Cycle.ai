CATALOG = [
    ("mood", "Mood", [
        "Calm", "Happy", "Energetic", "Frisky", "Mood swings", "Irritated", "Sad", "Anxious",
        "Depressed", "Feeling guilty", "Obsessive thoughts", "Low energy", "Apathetic",
        "Confused", "Very self-critical"], ""),
    ("symptoms", "Symptoms", [
        "Everything is fine", "Cramps", "Tender breasts", "Headache", "Acne", "Backache", "Fatigue",
        "Cravings", "Insomnia", "Abdominal pain", "Vaginal itching", "Vaginal dryness",
        "Hot flashes", "Night sweats", "Joint pain"], ""),
    ("discharge", "Vaginal discharge", [
        "No discharge", "Creamy", "Watery", "Sticky", "Egg white", "Spotting", "Unusual",
        "Clumpy white", "Gray"], ""),
    ("digestion", "Digestion and stool", ["Nausea", "Bloating", "Constipation", "Diarrhea"], ""),
    ("other", "Other", [
        "Travel", "Stress", "Meditation", "Journaling", "Kegel exercises", "Breathing exercises",
        "Disease or injury", "Alcohol"], ""),
    ("activity", "Physical activity", [
        "Didn't exercise", "Yoga", "Gym", "Aerobics & dancing", "Swimming", "Team sports",
        "Running", "Cycling", "Walking"], ""),
]

# chips that also become rows in the symptoms table (so charts and the Health Check see them)
SYMPTOM_MAP = {
    "Cramps": "cramps", "Tender breasts": "breast tenderness", "Headache": "headache",
    "Acne": "acne", "Backache": "back pain", "Fatigue": "fatigue", "Cravings": "cravings",
    "Insomnia": "insomnia", "Abdominal pain": "abdominal pain", "Vaginal itching": "vaginal itching",
    "Vaginal dryness": "vaginal dryness", "Hot flashes": "hot flashes", "Night sweats": "night sweats",
    "Joint pain": "joint pain", "Nausea": "nausea", "Bloating": "bloating", "Mood swings": "mood swings",
}

SYMPTOM_NAMES = set(SYMPTOM_MAP.values())

_TAG_CATEGORY = {}
for _key, _title, _tags, _hint in CATALOG:
    for _t in _tags:
        _TAG_CATEGORY.setdefault(_t, _key)

# symptom row name -> (category, chip label)
REVERSE = {SYMPTOM_MAP[t]: (_TAG_CATEGORY[t], t) for t in SYMPTOM_MAP}