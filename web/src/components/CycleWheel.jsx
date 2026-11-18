import { MARK_STYLE, MONTHS, dayClass, daysInMonth, periodLine, titleCase, toISO, today } from "../cycle.js";

/** Ring of this month's dates coloured like the calendar, with cycle info in the centre. */
export default function CycleWheel({ pred, marks }) {
  const now = today();
  const n = daysInMonth(now.getFullYear(), now.getMonth());
  const C = 200;
  const R = 158;
  const r = 13;
  const ok = pred && pred.status === "ok";

  const pos = (day) => {
    const a = ((-90 + ((day - 1) * 360) / n) * Math.PI) / 180;
    return [C + R * Math.cos(a), C + R * Math.sin(a)];
  };

  const line1 = now.getDate() + " " + MONTHS[now.getMonth()].slice(0, 3);
  const line2 = ok ? "Day " + pred.day_in_cycle : "Welcome";
  const line3 = ok ? titleCase(pred.current_phase) + " phase" : "Add your last period";
  const line4 = ok ? periodLine(pred) : "Tap + below to start";
  const [tx, ty] = pos(now.getDate());

  return (
    <svg className="wheel" viewBox="0 0 400 400" role="img" aria-label={`${line2}, ${line3}, ${line4}`}>
      <defs>
        <radialGradient id="wheelCore" cx="50%" cy="32%" r="75%">
          <stop offset="0%" stopColor="#ebaab9" />
          <stop offset="100%" stopColor="#a94a67" />
        </radialGradient>
        <linearGradient id="wheelGold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f1d6c8" /><stop offset="0.5" stopColor="#c8917f" /><stop offset="1" stopColor="#e6c2b3" />
        </linearGradient>
        <filter id="wheelShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="#a94a67" floodOpacity="0.28" />
        </filter>
      </defs>
      <circle cx={C} cy={C} r="192" fill="rgba(255,255,255,0.75)" />
      <circle cx={C} cy={C} r="130" fill="#fff" />
      <circle cx={C} cy={C} r="114" fill="none" stroke="url(#wheelGold)" strokeWidth="3" />
      {Array.from({ length: n }, (_, i) => {
        const day = i + 1;
        const iso = toISO(new Date(now.getFullYear(), now.getMonth(), day));
        const cls = ok ? dayClass(iso, marks) : "";
        const st = MARK_STYLE[cls];
        const [x, y] = pos(day);
        return (
          <g key={day} className="dot" style={{ animationDelay: day * 0.018 + "s" }}>
            <circle cx={x} cy={y} r={r} fill={st ? st.bg : "#fbf1f2"} />
            <text x={x} y={y + 4} fontSize="11" textAnchor="middle" fill={st ? st.fg : "#9a7f8d"} fontWeight={st ? 600 : 400}>
              {day}
            </text>
          </g>
        );
      })}
      <circle className="today-ring" cx={tx} cy={ty} r={r + 5} fill="none" stroke="#4a1838" strokeWidth="2.5" />
      <circle className="core" cx={C} cy={C} r="108" fill="url(#wheelCore)" filter="url(#wheelShadow)" />
      <path d="M200 112 C194 122 189 128 189 135 a11 11 0 0 0 22 0 C211 128 206 122 200 112Z" fill="#fff" opacity="0.9" />
      <text x={C} y="176" fontSize="14" textAnchor="middle" fill="#ffe3ed">{line1}</text>
      <text x={C} y="214" fontSize="42" fontWeight="700" textAnchor="middle" fill="#fff" fontFamily="Cormorant Garamond, Georgia, serif">{line2}</text>
      <text x={C} y="238" fontSize="15" textAnchor="middle" fill="#fff">{line3}</text>
      <text x={C} y="262" fontSize="13" textAnchor="middle" fill="#ffe3ed">{line4}</text>
    </svg>
  );
}

export function Legend() {
  return (
    <div className="legend">
      {Object.entries(MARK_STYLE).map(([k, v]) => (
        <span key={k}>
          <i style={{ background: v.bg }} />
          {v.label}
        </span>
      ))}
    </div>
  );
}
