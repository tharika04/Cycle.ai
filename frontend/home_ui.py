import math

PINK, DEEP = "#f0457a", "#d6336c"


def ring_svg(pred):
    """Progress ring for the cycle: day, phase and days until the next period."""
    R, SW = 118, 22
    C = 2 * math.pi * R
    if pred:
        L = max(int(pred["avg_cycle_length"]), 1)
        frac = min(max(int(pred["day_in_cycle"]) / L, 0.02), 1.0)
        line1 = "Day %d" % int(pred["day_in_cycle"])
        line2 = pred["current_phase"].title()
        left = int(pred["days_until_next_period"])
        line3 = "Period in %d days" % left if left > 0 else ("Period expected today" if left == 0 else "%d days late" % (-left))
    else:
        frac, line1, line2, line3 = 0.02, "Welcome", "Add your last period", "Tap + below"
    ang = -math.pi / 2 + 2 * math.pi * frac
    ex, ey = 150 + R * math.cos(ang), 150 + R * math.sin(ang)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">']
    s.append('<defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff8fb0"/>'
             '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % DEEP)
    s.append('<circle cx="150" cy="150" r="140" fill="#ffffff" opacity="0.55"/>')
    s.append('<circle cx="150" cy="150" r="%d" fill="none" stroke="#ffd3e2" stroke-width="%d"/>' % (R, SW))
    s.append('<circle cx="150" cy="150" r="%d" fill="none" stroke="url(#rg)" stroke-width="%d" stroke-linecap="round" '
             'stroke-dasharray="%.1f %.1f" transform="rotate(-90 150 150)"/>' % (R, SW, C * frac, C))
    s.append('<circle cx="%.1f" cy="%.1f" r="7" fill="#ffffff"/>' % (ex, ey))
    s.append('<path d="M150 70 C142 84 136 92 136 100 A14 14 0 0 0 164 100 C164 92 158 84 150 70 Z" fill="%s"/>' % PINK)
    s.append('<text x="150" y="152" font-size="46" font-weight="700" text-anchor="middle" fill="#2b1f26" font-family="Arial, sans-serif">%s</text>' % line1)
    s.append('<text x="150" y="182" font-size="20" font-weight="600" text-anchor="middle" fill="#2b1f26" font-family="Arial, sans-serif">%s</text>' % line2)
    s.append('<text x="150" y="208" font-size="15" text-anchor="middle" fill="#6d5a63" font-family="Arial, sans-serif">%s</text>' % line3)
    s.append("</svg>")
    return "".join(s)


CSS = """
<style>
.hh { display:flex; align-items:center; gap:0.8rem; }
.hh .av { width:54px; height:54px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#ffcf9f,#ff8fb0); color:#fff; font-weight:800; font-size:1.4rem;
  border:3px solid #ffffff; box-shadow:0 4px 12px rgba(214,90,140,0.25); flex:none; }
.hh .hi { font-weight:800; font-size:1.2rem; line-height:1.2; }
.hh .sub { color:#8a7f85; font-size:0.85rem; }
.st-key-homehead [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; align-items:center; }
.st-key-homehead [data-testid="stColumn"]:nth-child(2), .st-key-homehead [data-testid="column"]:nth-child(2)
  { flex:0 0 50px !important; min-width:50px !important; }
.st-key-homebell a { justify-content:center; width:46px; height:46px; padding:0; border-radius:50%;
  background:#ffffff; box-shadow:0 4px 12px rgba(214,90,140,0.20); }
.st-key-homebell a p { display:none; }
.np { display:flex; align-items:center; gap:1rem; }
.np .ic { width:56px; height:56px; border-radius:16px; background:#ffe3ec; display:flex; align-items:center;
  justify-content:center; font-size:1.7rem; flex:none; }
.np .sub { color:#6d5a63; font-size:0.85rem; }
.np .big { font-weight:800; font-size:1.6rem; line-height:1.15; color:#2b1f26; }
.np .exp { color:#8a7f85; font-size:0.78rem; }
.st-key-ring { display:flex; justify-content:center; }
.st-key-ring > div { display:flex; justify-content:center; width:100%; }
.cp { margin:0.4rem 0 0.8rem 0; padding:0.7rem 1rem; border-radius:18px; background:rgba(255,255,255,0.74); }
.cp .row { display:flex; justify-content:space-between; font-weight:600; font-size:0.9rem; margin-bottom:0.4rem; }
.cp .bar { height:10px; border-radius:6px; background:#ffd3e2; overflow:hidden; }
.cp .bar div { height:100%; border-radius:6px; background:linear-gradient(90deg,#ff8fb0,#d6336c); }
.st-key-hometiles [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:0.5rem; }
.st-key-hometiles [data-testid="stColumn"], .st-key-hometiles [data-testid="column"]
  { min-width:0 !important; flex:1 1 0 !important; width:auto !important; }
[class*="st-key-ht_"] { background:rgba(255,255,255,0.80); border-radius:18px; padding:0.7rem 0.2rem 0.4rem 0.2rem;
  box-shadow:0 6px 16px rgba(214,90,140,0.14); text-align:center; }
[class*="st-key-ht_"] .em { font-size:1.6rem; line-height:1.1; }
[class*="st-key-ht_"] a { justify-content:center; padding:0.1rem 0; }
[class*="st-key-ht_"] a p { font-size:0.72rem; font-weight:700; }
.tip { display:flex; align-items:center; gap:0.9rem; }
.tip .ic { width:48px; height:48px; border-radius:50%; background:#fff3d6; display:flex; align-items:center;
  justify-content:center; font-size:1.5rem; flex:none; }
.tip .t { font-weight:800; font-size:0.95rem; margin-bottom:0.1rem; }
.tip .d { color:#4b4448; font-size:0.85rem; }
</style>
"""