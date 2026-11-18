import random
from urllib.parse import quote

PINK, PINK2, PEACH, GREY, LAV = "#ff5c86", "#ff8fb0", "#f5d5bd", "#e6dcde", "#e3d6f7"


def _flower(cx, cy, r, petal, rot=0, n=6, op=1.0):
    g = ['<g opacity="%.2f" transform="translate(%.1f %.1f) rotate(%.1f)">' % (op, cx, cy, rot)]
    for i in range(n):
        g.append(
            '<ellipse cx="0" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" transform="rotate(%.1f)"/>'
            % (-r * 0.62, r * 0.28, r * 0.55, petal, i * 360 / n)
        )
    g.append('<circle r="%.1f" fill="#3a3336"/></g>' % (r * 0.2))
    return "".join(g)


def _daisy(cx, cy, r, rot=0, op=1.0):
    g = ['<g opacity="%.2f" transform="translate(%.1f %.1f) rotate(%.1f)">' % (op, cx, cy, rot)]
    for i in range(10):
        g.append(
            '<ellipse cx="0" cy="%.1f" rx="%.1f" ry="%.1f" fill="#ffffff" transform="rotate(%.1f)"/>'
            % (-r * 0.6, r * 0.16, r * 0.42, i * 36)
        )
    g.append('<circle r="%.1f" fill="#f7c948"/></g>' % (r * 0.22))
    return "".join(g)


def _petal(cx, cy, s, color, rot, op=0.75):
    return (
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity="%.2f" transform="rotate(%.1f %.1f %.1f)"/>'
        % (cx, cy, s * 0.45, s, color, op, rot, cx, cy)
    )


def banner_svg():
    flowers = [
        (215, 105, 62, PINK, 0), (385, 60, 40, PEACH, 20), (560, 120, 66, GREY, 12), (310, 215, 34, PINK2, 35),
        (480, 235, 28, PEACH, 8), (130, 215, 38, PEACH, 15), (640, 250, 30, PINK, 40), (95, 80, 28, GREY, 10),
        (40, 170, 30, PINK2, 25), (715, 70, 34, PINK2, 5), (610, 35, 22, PEACH, 30), (170, 30, 24, GREY, 18),
        (380, 270, 22, PINK2, 0), (700, 190, 20, PEACH, 12),
    ]
    body = "".join(_flower(x, y, r, c, rot) for x, y, r, c, rot in flowers)
    body += _daisy(420, 150, 26, 10) + _daisy(90, 140, 18, 20) + _daisy(560, 250, 20, 0) + _daisy(260, 120, 16, 30)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300">' + body + "</svg>"


def tile_svg():
    rnd = random.Random(11)
    size, cell = 900, 225
    colors = [PINK2, PEACH, GREY, PINK, LAV, PEACH, PINK2]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (size, size, size, size)]
    k = 0
    for i in range(4):
        for j in range(4):
            r = rnd.randint(20, 42)
            x = min(max((i + 0.5) * cell + rnd.randint(-55, 55), r + 6), size - r - 6)
            y = min(max((j + 0.5) * cell + rnd.randint(-55, 55), r + 6), size - r - 6)
            parts.append(_flower(x, y, r, colors[k % len(colors)], rnd.randint(0, 60), op=0.5))
            k += 1
    for _ in range(7):
        r = rnd.randint(14, 22)
        parts.append(_daisy(rnd.randint(r + 6, size - r - 6), rnd.randint(r + 6, size - r - 6), r, rnd.randint(0, 30), 0.9))
    for _ in range(36):
        s = rnd.randint(8, 15)
        parts.append(
            _petal(rnd.randint(16, size - 16), rnd.randint(16, size - 16), s,
                   rnd.choice([PINK2, PEACH, LAV, "#ffd1de"]), rnd.randint(0, 180))
        )
    parts.append("</svg>")
    return "".join(parts)


def css():
    tile = "data:image/svg+xml," + quote(tile_svg(), safe="")
    return (
        "<style>"
        '.stApp { background: url("' + tile + '") 0 0 / 900px 900px repeat, '
        "linear-gradient(180deg, #ffe9f1 0%, #fff6f9 45%, #ffeef4 100%) !important; }"
        ".hello-big { text-shadow: 0 0 18px #ffffff, 0 0 8px #ffffff; }"
        ".tagline { text-shadow: 0 0 10px #ffffff, 0 0 6px #ffffff; color:#6d6469; }"
        '[data-testid="stForm"] { border: 3px solid #ff3d7f !important; border-radius: 26px !important;'
        " background: #ffffff !important; padding: 1.4rem !important;"
        " box-shadow: 0 0 0 5px rgba(255,143,176,0.35), 0 10px 28px rgba(240,69,122,0.25) !important; }"
        '[data-testid="stForm"] [data-baseweb="input"] { border: 1.6px solid #ff8fb0 !important; border-radius: 14px !important; }'
        '[data-testid="stForm"] [data-baseweb="input"]:focus-within { border-color: #ff3d7f !important;'
        " box-shadow: 0 0 0 3px rgba(255,61,127,0.18) !important; }"
        ".stTabs [data-baseweb=\"tab-list\"] { background: rgba(255,255,255,0.65); border-radius: 14px; padding: 0.2rem 0.6rem; }"
        "</style>"
    )