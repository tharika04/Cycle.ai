import math
from functools import lru_cache

FY = 203
LT, NK = 56, 20
TH, SH = 52, 48
UA, FA = 30, 28

SKIN = "#f0b394"
SKIN_FAR = "#dd9c7e"
TOP = "#ff7aa2"
LEG = "#7b6bd6"
LEG_FAR = "#5d4fb5"
HAIR = "#3b2a2a"
BG = "#fff5f8"
FLOOR = "#ecc9d6"


def ik(root, target, l1, l2, bend):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d0 = math.hypot(dx, dy) or 0.001
    ux, uy = dx / d0, dy / d0
    d = max(min(d0, l1 + l2 - 0.01), abs(l1 - l2) + 0.01)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    bx, by = root[0] + ux * a, root[1] + uy * a
    mid = (bx + bend * (-uy) * h, by + bend * ux * h)
    end = (root[0] + ux * d, root[1] + uy * d)
    return mid, end


def _target(t, pts):
    if isinstance(t, str):
        return pts[t]
    if isinstance(t[0], str):
        if t[0] in ("K1", "K2"):
            return pts[t[0]]
        base = pts[t[0]]
        return (base[0] + t[1], base[1] + t[2])
    return t


def solve(spec, pose):
    P = spec["P"]
    ta = math.radians(spec["ta"])
    ux, uy = math.cos(ta), -math.sin(ta)
    N = (P[0] + LT * ux, P[1] + LT * uy)
    ha = math.radians(spec["ha"])
    H = (N[0] + NK * math.cos(ha), N[1] - NK * math.sin(ha))
    nx, ny = uy, -ux
    if ny > 0:
        nx, ny = -nx, -ny
    c = spec.get("curve", 0)
    M = ((P[0] + N[0]) / 2 + nx * c, (P[1] + N[1]) / 2 + ny * c)
    vx, vy = -uy, ux
    sx, hx = pose.get("sx", 0), pose.get("hx", 0)
    S1 = (N[0] - vx * sx, N[1] - vy * sx)
    S2 = (N[0] + vx * sx, N[1] + vy * sx)
    L1 = (P[0] - vx * hx, P[1] - vy * hx)
    L2 = (P[0] + vx * hx, P[1] + vy * hx)
    pts = {"P": P, "N": N, "H": H, "M": M, "S1": S1, "S2": S2, "L1": L1, "L2": L2}
    K1, F1 = ik(L1, _target(spec["F1"], pts), TH, SH, pose["kb1"])
    K2, F2 = ik(L2, _target(spec["F2"], pts), TH, SH, pose["kb2"])
    pts.update({"K1": K1, "F1": F1, "K2": K2, "F2": F2})
    E1, W1 = ik(S1, _target(spec["W1"], pts), UA, FA, pose["eb1"])
    E2, W2 = ik(S2, _target(spec["W2"], pts), UA, FA, pose["eb2"])
    pts.update({"E1": E1, "W1": W1, "E2": E2, "W2": W2})
    return pts


def _lerp(a, b, t):
    return a + (b - a) * t


def interp(A, B, t):
    out = {}
    for k in A:
        a, b = A[k], B[k]
        if isinstance(a, (int, float)):
            out[k] = _lerp(a, b, t)
        elif isinstance(a, str):
            out[k] = a
        elif isinstance(a[0], str):
            out[k] = a if len(a) == 1 else (a[0], _lerp(a[1], b[1], t), _lerp(a[2], b[2], t))
        else:
            out[k] = (_lerp(a[0], b[0], t), _lerp(a[1], b[1], t))
    return out


def full(spec):
    s = dict(spec)
    s.setdefault("curve", 0)
    s.setdefault("F2", s["F1"])
    s.setdefault("W2", s["W1"])
    return s


# angles: degrees, 0 = right, 90 = up. kb/eb: knee/elbow bend side (+1/-1)
POSES = {
    "childs": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=6,
        A=dict(P=(80, 163), ta=-8, ha=-35, F1=(70, 198), W1=(220, 198), W2=(212, 198)),
        B=dict(P=(80, 157), ta=2, ha=-25, F1=(70, 198), W1=(220, 198), W2=(212, 198))),
    "widechild": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=6,
        A=dict(P=(86, 164), ta=-4, ha=-30, F1=(76, 198), W1=(250, 198), W2=(240, 198)),
        B=dict(P=(70, 166), ta=-14, ha=-40, F1=(62, 198), W1=(250, 198), W2=(240, 198))),
    "catcow": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=6,
        A=dict(P=(100, 145), ta=6, ha=-60, curve=18, F1=(54, 198), W1=(156, 198)),
        B=dict(P=(100, 145), ta=6, ha=38, curve=-14, F1=(54, 198), W1=(156, 198))),
    "needle": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=6,
        A=dict(P=(100, 145), ta=6, ha=15, F1=(54, 198), W1=(156, 198), W2=(156, 198)),
        B=dict(P=(100, 145), ta=-14, ha=-80, F1=(54, 198), W1=(156, 198), W2=(118, 198))),
    "bridge": dict(
        kb1=-1, kb2=-1, eb1=-1, eb2=-1, dur=5,
        A=dict(P=(185, 192), ta=180, ha=180, F1=(235, 198), W1=(190, 198)),
        B=dict(P=(185, 160), ta=215, ha=180, F1=(235, 198), W1=(197, 198))),
    "glute": dict(
        kb1=-1, kb2=-1, eb1=-1, eb2=-1, dur=5,
        A=dict(P=(185, 192), ta=180, ha=180, F1=(235, 198), W1=(190, 198)),
        B=dict(P=(185, 150), ta=228, ha=180, F1=(235, 198), W1=(197, 198))),
    "cobra": dict(
        kb1=1, kb2=1, eb1=-1, eb2=-1, dur=5,
        A=dict(P=(130, 194), ta=0, ha=0, F1=(30, 198), W1=(172, 198)),
        B=dict(P=(130, 194), ta=25, ha=40, F1=(30, 198), W1=(178, 198))),
    "kneeschest": dict(
        kb1=-1, kb2=-1, eb1=-1, eb2=-1, dur=5,
        A=dict(P=(190, 192), ta=180, ha=180, F1=(290, 198), W1="K1"),
        B=dict(P=(190, 192), ta=180, ha=180, F1=(205, 168), W1="K1")),
    "fold": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=6,
        A=dict(P=(110, 194), ta=90, ha=90, F1=(205, 198), W1=(150, 192)),
        B=dict(P=(110, 194), ta=15, ha=-20, F1=(205, 198), W1=(200, 196))),
    "march": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=2.4, hold=1, sx=0,
        A=dict(P=(160, 102), ta=90, ha=90, F1=(172, 150), F2=(160, 200),
               W1=("N", -16, 34), W2=("N", 18, 30)),
        B=dict(P=(160, 102), ta=90, ha=90, F1=(160, 200), F2=(172, 150),
               W1=("N", 18, 30), W2=("N", -16, 34))),
    "sidebend": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=-1, dur=4.5, sx=9, hx=8,
        A=dict(P=(160, 102), ta=106, ha=106, F1=(146, 200), F2=(174, 200),
               W1=("N", -24, -46), W2=("N", 22, 40)),
        B=dict(P=(160, 102), ta=74, ha=74, F1=(146, 200), F2=(174, 200),
               W1=("N", -22, 40), W2=("N", 24, -46))),
    "squat": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=4.5,
        A=dict(P=(165, 102), ta=90, ha=90, F1=(165, 200), W1=("N", 55, 8)),
        B=dict(P=(135, 150), ta=65, ha=80, F1=(165, 200), W1=("N", 55, 5))),
    "wallpush": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=1, dur=4, decor="wall",
        A=dict(P=(166.7, 135.1), ta=39, ha=39, F1=(89, 200), W1=(268, 100)),
        B=dict(P=(174.7, 146.5), ta=31, ha=31, F1=(89, 200), W1=(268, 100))),
    "breathe": dict(
        kb1=-1, kb2=-1, eb1=-1, eb2=-1, dur=8, decor="breath",
        A=dict(P=(185, 192), ta=180, ha=180, curve=0, F1=(235, 198), W1=("P", -22, -12)),
        B=dict(P=(185, 192), ta=180, ha=180, curve=7, F1=(235, 198), W1=("P", -22, -16))),
    "twist_a": dict(
        kb1=1, kb2=1, eb1=1, eb2=-1, dur=6, decor="mat",
        A=dict(P=(170, 110), ta=180, ha=180, F1=(268, 106), F2=(268, 114),
               W1=(114, 52), W2=(114, 168)),
        B=dict(P=(170, 110), ta=180, ha=180, F1=(214, 172), F2=(224, 176),
               W1=(114, 52), W2=(114, 168))),
    "twist_b": dict(
        kb1=-1, kb2=-1, eb1=1, eb2=-1, dur=6, decor="mat",
        A=dict(P=(170, 110), ta=180, ha=180, F1=(268, 106), F2=(268, 114),
               W1=(114, 52), W2=(114, 168)),
        B=dict(P=(170, 110), ta=180, ha=180, F1=(214, 50), F2=(224, 46),
               W1=(114, 52), W2=(114, 168))),
}


for _k in ("childs", "widechild", "catcow", "needle", "bridge", "glute",
           "cobra", "kneeschest", "fold", "breathe"):
    POSES[_k]["view"] = (60, 160)


def _frames(pose, n=10):
    hold = pose.get("hold", 3)
    A, B = full(pose["A"]), full(pose["B"])
    seq = [0.0] * hold + [i / n for i in range(1, n)] + [1.0] * hold + [i / n for i in range(n - 1, 0, -1)]
    return [solve(interp(A, B, (1 - math.cos(math.pi * s)) / 2), pose) for s in seq], hold, n


@lru_cache(maxsize=None)
def svg(key):
    pose = POSES[key]
    frames, hold, n = _frames(pose)
    total = len(frames)
    dur = pose["dur"]
    first = frames[0]
    decor = pose.get("decor", "floor")

    def poly(names, color, width):
        vals = ";".join(" ".join("%.1f,%.1f" % f[nm] for nm in names) for f in frames)
        start = " ".join("%.1f,%.1f" % first[nm] for nm in names)
        return (
            '<polyline fill="none" stroke="%s" stroke-width="%d" stroke-linecap="round" '
            'stroke-linejoin="round" points="%s"><animate attributeName="points" dur="%ss" '
            'repeatCount="indefinite" values="%s"/></polyline>' % (color, width, start, dur, vals)
        )

    def dot(name, dx, dy, r, color):
        xs = ";".join("%.1f" % (f[name][0] + dx) for f in frames)
        ys = ";".join("%.1f" % (f[name][1] + dy) for f in frames)
        return (
            '<circle r="%d" fill="%s" cx="%.1f" cy="%.1f">'
            '<animate attributeName="cx" dur="%ss" repeatCount="indefinite" values="%s"/>'
            '<animate attributeName="cy" dur="%ss" repeatCount="indefinite" values="%s"/></circle>'
            % (r, color, first[name][0] + dx, first[name][1] + dy, dur, xs, dur, ys)
        )

    vy, vh = pose.get("view", (-24, 244))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 %d 320 %d">' % (vy, vh)]
    out.append('<rect x="0" y="%d" width="320" height="%d" rx="24" fill="%s"/>' % (vy, vh, BG))
    if decor == "mat":
        out.append('<rect x="30" y="30" width="270" height="160" rx="18" fill="#f3d9e3"/>')
    else:
        out.append(
            '<line x1="10" y1="%d" x2="310" y2="%d" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
            % (FY, FY, FLOOR)
        )
    if decor == "wall":
        out.append('<rect x="270" y="20" width="10" height="%d" rx="3" fill="#e6d3db"/>' % (FY - 20))
    if decor == "breath":
        k1 = hold / total
        k2 = (hold + n - 1) / total
        k3 = (2 * hold + n - 1) / total
        out.append(
            '<circle cx="170" cy="140" r="14" fill="#ffe0ea"><animate attributeName="r" dur="%ss" '
            'repeatCount="indefinite" values="14;14;26;26;14" keyTimes="0;%.3f;%.3f;%.3f;1"/></circle>'
            % (dur, k1, k2, k3)
        )
    out.append(poly(["L2", "K2", "F2"], LEG_FAR, 11))
    out.append(poly(["S2", "E2", "W2"], SKIN_FAR, 8))
    out.append(poly(["P", "M", "N"], TOP, 16))
    out.append(poly(["L1", "K1", "F1"], LEG, 11))
    out.append(poly(["S1", "E1", "W1"], SKIN, 8))
    # long ponytail + pink hair tie so the figure reads as a woman
    def ponytail():
        offs = [(-6, -8), (-15, -6), (-21, 2), (-22, 13), (-19, 23)]

        def pts(f):
            hx, hy = f["H"]
            return " ".join("%.1f,%.1f" % (hx + dx, min(hy + dy, FY - 4)) for dx, dy in offs)

        vals = ";".join(pts(f) for f in frames)
        return (
            '<polyline fill="none" stroke="%s" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" '
            'points="%s"><animate attributeName="points" dur="%ss" repeatCount="indefinite" values="%s"/></polyline>'
            % (HAIR, pts(first), dur, vals)
        )

    out.append(ponytail())
    out.append(dot("H", -6, -3, 11, HAIR))
    out.append(dot("H", 0, 0, 10, SKIN))
    out.append(dot("H", -9, -8, 5, HAIR))
    out.append(dot("H", -15, -7, 3, TOP))
    out.append("</svg>")
    return "".join(out)