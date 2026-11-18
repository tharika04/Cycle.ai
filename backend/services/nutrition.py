PLANS = {
    "menstrual": {
        "title": "Menstrual phase (bleeding days)",
        "focus": "Replace iron, ease cramps and fatigue.",
        "foods_common": [
            "Spinach (palak), beetroot, pomegranate, dates",
            "Dal, lentils, rajma, chickpeas",
            "Ragi and other millets",
            "Warm soups, ginger tea, bananas",
            "Lemon or amla with meals (vitamin C helps iron absorption)",
        ],
        "foods_by_diet": {
            "vegetarian": ["Paneer, curd, sesame seeds (til)", "A little jaggery"],
            "non-vegetarian": ["Eggs, chicken, fish (iron and omega-3)"],
            "vegan": ["Tofu, pumpkin seeds, fortified cereals", "Soaked chana and nuts"],
        },
        "limit": ["Too much caffeine", "Very salty or processed snacks", "Sugary drinks"],
        "exercise": {
            "intensity": "Low",
            "duration": "20-30 minutes, or rest if you feel drained",
            "activities": [
                "Easy walking",
                "Gentle yoga (child's pose, cat-cow, supine twist)",
                "Light stretching",
                "Slow cycling",
            ],
        },
        "tips": [
            "A heat pad on the lower abdomen can ease cramps.",
            "Drink water and warm fluids through the day.",
            "Prioritize sleep; fatigue is common on heavy days.",
        ],
    },
    "follicular": {
        "title": "Follicular phase (after your period)",
        "focus": "Energy is rising. Support it with protein, fiber, and fresh foods.",
        "foods_common": [
            "Sprouts, oats, broccoli, mixed vegetables",
            "Berries, citrus fruits, apples",
            "Nuts and seeds (flax, pumpkin)",
            "Millets, brown rice, whole wheat",
            "Fermented foods like idli and dosa batter dishes",
        ],
        "foods_by_diet": {
            "vegetarian": ["Curd, buttermilk, paneer"],
            "non-vegetarian": ["Eggs, chicken, fish"],
            "vegan": ["Tofu, tempeh, soy milk, mixed legumes"],
        },
        "limit": ["Heavy fried food", "Excess refined sugar"],
        "exercise": {
            "intensity": "Moderate to high",
            "duration": "30-45 minutes",
            "activities": [
                "Strength training",
                "Jogging or brisk walking",
                "Dance or aerobics",
                "A good time to try a new workout",
            ],
        },
        "tips": [
            "Energy and mood often improve, so plan demanding tasks now.",
            "Eat protein with each meal to support muscle recovery.",
        ],
    },
    "ovulation": {
        "title": "Ovulation phase (fertile window)",
        "focus": "Peak energy for many people. Focus on antioxidants, fiber, and hydration.",
        "foods_common": [
            "Leafy greens, tomatoes, bell peppers, cucumber",
            "Fruits like papaya, berries, oranges",
            "Quinoa, brown rice, whole grains",
            "Almonds and walnuts",
            "Plenty of water and coconut water",
        ],
        "foods_by_diet": {
            "vegetarian": ["Curd, paneer"],
            "non-vegetarian": ["Fish, eggs"],
            "vegan": ["Chickpeas, lentils, flax seeds"],
        },
        "limit": ["Alcohol", "Too much salt"],
        "exercise": {
            "intensity": "High (if you feel good)",
            "duration": "30-60 minutes",
            "activities": [
                "HIIT or running",
                "Heavier strength training",
                "Group sports or classes",
                "Warm up well before intense sessions",
            ],
        },
        "tips": [
            "You may feel more social and energetic.",
            "Stay hydrated, especially with intense workouts.",
        ],
    },
    "luteal": {
        "title": "Luteal phase (before your period)",
        "focus": "Manage PMS, cravings, and mood with magnesium, calcium, and complex carbs.",
        "foods_common": [
            "Sweet potato, bananas, oats, brown rice, millets",
            "Pumpkin seeds, almonds, walnuts (magnesium)",
            "Leafy greens and dal",
            "A small piece of dark chocolate",
            "Small, regular meals to keep energy steady",
        ],
        "foods_by_diet": {
            "vegetarian": ["Milk, curd, paneer (calcium)"],
            "non-vegetarian": ["Eggs, fish like salmon or sardines"],
            "vegan": ["Tofu, chickpeas, fortified plant milk"],
        },
        "limit": ["Excess salt (bloating)", "Caffeine", "Sugary snacks", "Alcohol"],
        "exercise": {
            "intensity": "Moderate, easing off near your period",
            "duration": "20-40 minutes",
            "activities": [
                "Pilates or yoga",
                "Swimming",
                "Moderate strength training",
                "Walking",
            ],
        },
        "tips": [
            "Cravings are common; pair sweet snacks with protein or fiber.",
            "Aim for steady sleep; poor sleep can worsen PMS.",
            "Light exercise and stretching can help mood and bloating.",
        ],
    },
}

DIETS = ["vegetarian", "non-vegetarian", "vegan"]
DISCLAIMER = (
    "General wellness information, not medical advice. "
    "Talk to a doctor or dietitian about allergies, anemia, PCOS, or other conditions."
)


def build_plan(phase, diet):
    phase = "luteal" if phase == "late" else phase
    if phase not in PLANS:
        raise ValueError("Unknown phase")
    if diet not in DIETS:
        raise ValueError("Unknown diet")
    p = PLANS[phase]
    return {
        "phase": phase,
        "diet": diet,
        "title": p["title"],
        "focus": p["focus"],
        "eat": p["foods_common"] + p["foods_by_diet"][diet],
        "limit": p["limit"],
        "exercise": p["exercise"],
        "tips": p["tips"],
        "disclaimer": DISCLAIMER,
    }