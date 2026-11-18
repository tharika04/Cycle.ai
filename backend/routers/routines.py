from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.services import figures

router = APIRouter(prefix="/routines", tags=["routines"])

# (name, seconds, animation key, tip)
ROUTINES = {
    "wake": {
        "title": "Wake-Up Routine",
        "poses": [
            ("Child's Pose", 30, "childs", "Put a pillow under your chest if it feels tight."),
            ("Cat-Cow", 30, "catcow", "Move slowly with your breath."),
            ("Half Bridge", 30, "bridge", "Lift only as high as feels comfortable."),
            ("Low Cobra", 30, "cobra", "Keep it low, and skip it if it feels uncomfortable on your belly."),
            ("Reclined Twist", 30, "twist_a", "Let gravity do the work."),
        ],
    },
    "back": {
        "title": "Back Stretch",
        "poses": [
            ("Knees to Chest", 40, "kneeschest", "Keep your neck and shoulders loose."),
            ("Thread the Needle", 40, "needle", "Stay where it feels like a stretch, not a strain."),
            ("Seated Forward Fold", 40, "fold", "Bend your knees as much as you need."),
            ("Lying Spinal Twist", 40, "twist_b", "Support your knees with a pillow if they do not reach the floor."),
            ("Wide-Arm Child's Pose", 40, "widechild", "Breathe into your lower back."),
        ],
    },
    "body": {
        "title": "Body Workout",
        "poses": [
            ("March in Place", 40, "march", "Lower the pace if you feel tired."),
            ("Standing Side Bend", 40, "sidebend", "Keep both feet firmly on the floor."),
            ("Easy Squats", 40, "squat", "Hold a chair for balance if you like."),
            ("Wall Push-Ups", 40, "wallpush", "Step closer to the wall to make it easier."),
            ("Glute Bridge", 40, "glute", "Do not arch your lower back."),
            ("Deep Breathing", 40, "breathe", "Lie on your back with a hand on your belly. Breathe in for 4, out for 6."),
        ],
    },
}


@router.get("")
def list_routines():
    out = []
    for key, r in ROUTINES.items():
        poses = [{"name": n, "seconds": s, "figure": a, "tip": t} for n, s, a, t in r["poses"]]
        out.append({
            "key": key,
            "title": r["title"],
            "total_seconds": sum(p["seconds"] for p in poses),
            "poses": poses,
        })
    return out


@router.get("/figure/{name}")
def figure(name: str):
    if name not in figures.POSES:
        raise HTTPException(status_code=404, detail="Unknown pose")
    return Response(
        content=figures.svg(name),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )
