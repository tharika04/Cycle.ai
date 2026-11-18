import time

import streamlit as st

import figures

ROUTINES = {
    "wake": {
        "title": "Wake-Up Routine",
        "icon": "\U0001F305",
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
        "icon": "\U0001F9D8\u200D\u2640\uFE0F",
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
        "icon": "\U0001F4AA",
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

CSS = """
<style>
.r-icon { font-size: 2.4rem; line-height: 1; }
.r-title { font-weight: 700; margin: 0.4rem 0 0.1rem 0; }
.r-sub { font-size: 0.78rem; color: #6d6469; margin-bottom: 0.4rem; }
[class*="st-key-routines"] [data-testid="stHorizontalBlock"],
[class*="st-key-rnav"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.5rem; }
[class*="st-key-routines"] [data-testid="stColumn"], [class*="st-key-routines"] [data-testid="column"],
[class*="st-key-rnav"] [data-testid="stColumn"], [class*="st-key-rnav"] [data-testid="column"] {
  min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }
[class*="st-key-rcard_"] {
  border-radius: 22px; padding: 1rem 0.8rem 0.5rem 0.8rem; min-height: 170px;
  border: 2px solid #ffd6e3; box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05); }
[class*="st-key-rcard_wake"] { background: linear-gradient(160deg, #fff4e8, #ffd9b8); border-color: #ffc994; }
[class*="st-key-rcard_back"] { background: linear-gradient(160deg, #f6efff, #e2d2ff); border-color: #d0b8ff; }
[class*="st-key-rcard_body"] { background: linear-gradient(160deg, #fff0f5, #ffd0e0); border-color: #ffb3c7; }
.pose-name { font-weight: 700; font-size: 1.05rem; margin-top: 0.4rem; }
.pose-meta { font-size: 0.8rem; color: #8a7f85; margin-bottom: 0.8rem; }
.g-name { font-size: 1.4rem; font-weight: 700; text-align: center; margin: 0.4rem 0; }
.g-timer { font-size: 2.6rem; font-weight: 800; text-align: center; color: #f0457a; }
</style>
"""


def total_seconds(key):
    return sum(p[1] for p in ROUTINES[key]["poses"])


def pick(key):
    st.session_state["rt_sel"] = key
    st.session_state["rt_guided"] = False
    st.session_state["rt_step"] = 0


def start():
    st.session_state["rt_guided"] = True
    st.session_state["rt_step"] = 0


def end():
    st.session_state["rt_guided"] = False
    st.session_state["rt_step"] = 0


def go(n):
    sel = st.session_state.get("rt_sel")
    count = len(ROUTINES[sel]["poses"]) if sel in ROUTINES else 0
    st.session_state["rt_step"] = max(0, min(count, st.session_state.get("rt_step", 0) + n))


def guided(key):
    poses = ROUTINES[key]["poses"]
    count = len(poses)
    step = st.session_state.get("rt_step", 0)

    if step >= count:
        st.success("Well done! You finished the routine.")
        st.caption("Drink some water and rest if you need to.")
        st.button("Close", key="rt_close", on_click=end)
        return

    name, seconds, anim, tip = poses[step]
    st.progress(step / count, text="Pose " + str(step + 1) + " of " + str(count))
    st.image(figures.svg(anim), width=340)
    st.markdown("<div class='g-name'>" + name + "</div>", unsafe_allow_html=True)
    st.caption("Tip: " + tip + "  |  Hold for " + str(seconds) + " seconds")

    timer = st.empty()
    timer.markdown("<div class='g-timer'>" + str(seconds) + "s</div>", unsafe_allow_html=True)

    with st.container(key="rnav"):
        c1, c2, c3 = st.columns(3)
        c1.button("\u25C0 Back", key="rt_back_" + str(step), on_click=go, args=(-1,), disabled=step == 0)
        started = c2.button("\u23F1 Timer", key="rt_timer_" + str(step))
        c3.button("Next \u25B6", key="rt_next_" + str(step), on_click=go, args=(1,))
    st.button("End routine", key="rt_end_" + str(step), on_click=end)

    if started:
        for s in range(seconds, 0, -1):
            timer.markdown("<div class='g-timer'>" + str(s) + "s</div>", unsafe_allow_html=True)
            time.sleep(1)
        timer.markdown("<div class='g-timer'>Done</div>", unsafe_allow_html=True)


def detail(key):
    r = ROUTINES[key]
    with st.container(key="rdetail"):
        st.markdown("### " + r["title"])
        st.caption(str(total_seconds(key)) + " seconds \u00B7 " + str(len(r["poses"])) + " poses")
        if st.session_state.get("rt_guided"):
            guided(key)
            return
        for i, (name, seconds, anim, tip) in enumerate(r["poses"], 1):
            st.image(figures.svg(anim), width=340)
            st.markdown(
                "<div class='pose-name'>" + str(i) + ". " + name + "</div>"
                "<div class='pose-meta'>Hold " + str(seconds) + " seconds \u00B7 " + tip + "</div>",
                unsafe_allow_html=True,
            )
        st.button("\u25B6 Start", key="rt_start", on_click=start)


def render():
    st.markdown(CSS, unsafe_allow_html=True)
    st.write("")
    st.subheader("Cramp relief routines")
    st.caption(
        "Gentle movement may help ease cramps for some people. Stop if anything hurts, "
        "and see a doctor for severe or unusual pain."
    )

    keys = list(ROUTINES)
    with st.container(key="routines"):
        for i in range(0, len(keys), 2):
            cols = st.columns(2)
            for col, k in zip(cols, keys[i:i + 2]):
                r = ROUTINES[k]
                with col:
                    with st.container(key="rcard_" + k):
                        st.markdown(
                            "<div class='r-icon'>" + r["icon"] + "</div>"
                            "<div class='r-title'>" + r["title"] + "</div>"
                            "<div class='r-sub'>" + str(total_seconds(k)) + " seconds \u00B7 "
                            + str(len(r["poses"])) + " poses</div>",
                            unsafe_allow_html=True,
                        )
                        st.button("View routine", key="rt_pick_" + k, on_click=pick, args=(k,))

    selected = st.session_state.get("rt_sel")
    if selected in ROUTINES:
        detail(selected)