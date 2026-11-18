import { useMemo, useState } from "react";
import { api } from "../api.js";
import { Bars, ErrorBox, Loading, Screen, TopBar, celebrate, useAsync, useToast } from "../components/ui.jsx";
import { fmtDate, titleCase, toISO, today } from "../cycle.js";

// [area, x, y] on a 100 x 200 figure
const FRONT = [
  ["Head", 50, 15], ["Neck", 50, 27], ["Chest or breasts", 50, 45], ["Upper abdomen", 50, 68],
  ["Lower abdomen", 50, 95], ["Pelvic area", 50, 112], ["Arms", 15, 72], ["Arms", 85, 72],
  ["Thighs", 38, 145], ["Thighs", 62, 145], ["Legs", 41, 180], ["Legs", 59, 180],
];
const BACK = [
  ["Head", 50, 15], ["Neck", 50, 27], ["Upper back", 50, 50], ["Lower back", 50, 88],
  ["Hips and buttocks", 50, 114], ["Arms", 15, 72], ["Arms", 85, 72],
  ["Thighs", 38, 145], ["Thighs", 62, 145], ["Legs", 41, 180], ["Legs", 59, 180],
];
const ALL = [...new Set([...FRONT, ...BACK].map((z) => z[0]))].sort();

function Figure({ zones, picked, toggle }) {
  return (
    <svg className="body-map" viewBox="0 0 100 200" role="group" aria-label="Body map">
      <g fill="#f6e1e4" stroke="#d9a99a" strokeWidth="0.8">
        <circle cx="50" cy="15" r="10" />
        <rect x="46" y="24" width="8" height="8" />
        <path d="M30 32 L70 32 L64 85 L72 115 L28 115 L36 85 Z" />
        <path d="M30 32 L23 32 L10 88 L17 91 L28 52 Z" />
        <path d="M70 32 L77 32 L90 88 L83 91 L72 52 Z" />
        <path d="M28 115 L49 115 L47 196 L36 196 Z" />
        <path d="M51 115 L72 115 L64 196 L53 196 Z" />
      </g>
      {zones.map(([name, x, y], i) => {
        const on = picked.has(name);
        return (
          <circle
            key={i}
            className="zone"
            cx={x}
            cy={y}
            r="7"
            fill={on ? "#a94a67" : "#dc96a6"}
            opacity={on ? 0.95 : 0.45}
            stroke="#fff"
            strokeWidth="1.2"
            onClick={() => toggle(name)}
            role="checkbox"
            aria-checked={on}
            aria-label={name}
            tabIndex={0}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && toggle(name)}
          >
            <title>{name}</title>
          </circle>
        );
      })}
    </svg>
  );
}

export default function BodyMap() {
  const toast = useToast();
  const [side, setSide] = useState("front");
  const [picked, setPicked] = useState(new Set());
  const [day, setDay] = useState(toISO(today()));
  const [severity, setSeverity] = useState(3);
  const [busy, setBusy] = useState(false);
  const [warn, setWarn] = useState(false);
  const history = useAsync(() => api.symptoms());

  const toggle = (name) =>
    setPicked((p) => {
      const n = new Set(p);
      n.has(name) ? n.delete(name) : n.add(name);
      return n;
    });

  const save = async () => {
    setBusy(true);
    try {
      for (const area of picked) {
        await api.addSymptom({ date: day, symptom: "pain - " + area.toLowerCase(), severity, mood: null });
      }
      toast("Saved pain for " + [...picked].join(", "));
      celebrate();
      setWarn(severity >= 5);
      setPicked(new Set());
      history.reload();
    } catch (e) {
      toast(e.message);
    } finally {
      setBusy(false);
    }
  };

  const pain = useMemo(() => (history.data || []).filter((s) => s.symptom.startsWith("pain - ")), [history.data]);
  const summary = useMemo(() => {
    const m = {};
    pain.forEach((s) => {
      const a = titleCase(s.symptom.slice(7));
      m[a] = m[a] || { n: 0, sev: 0 };
      m[a].n += 1;
      m[a].sev += s.severity;
    });
    return Object.entries(m)
      .map(([label, v]) => ({ label, value: v.n, avg: v.sev / v.n }))
      .sort((a, b) => b.value - a.value);
  }, [pain]);

  return (
    <Screen>
      <TopBar title="Pain Body Map" subtitle="Tap where it hurts, then save" />
      <div className="seg" style={{ marginBottom: 12 }}>
        <button className={side === "front" ? "on" : ""} onClick={() => setSide("front")}>Front</button>
        <button className={side === "back" ? "on" : ""} onClick={() => setSide("back")}>Back</button>
      </div>
      <div className="card">
        <Figure zones={side === "front" ? FRONT : BACK} picked={picked} toggle={toggle} />
      </div>

      <div className="card">
        <div className="field">
          <span>Or pick areas from a list</span>
          <div className="chips">
            {ALL.map((a) => (
              <button key={a} className={"chip" + (picked.has(a) ? " on" : "")} onClick={() => toggle(a)}>{a}</button>
            ))}
          </div>
        </div>
        <label className="field">
          <span>Date</span>
          <input className="input" type="date" max={toISO(today())} value={day} onChange={(e) => setDay(e.target.value)} />
        </label>
        <div className="row between" style={{ fontWeight: 600, fontSize: "0.85rem", color: "var(--plum)" }}>
          <span>Pain severity</span><span>{severity}/5</span>
        </div>
        <input type="range" min="1" max="5" value={severity} onChange={(e) => setSeverity(Number(e.target.value))} />
        <button className="btn block" style={{ marginTop: 12 }} disabled={!picked.size || busy} onClick={save}>
          {busy ? "Saving..." : picked.size ? "Save pain (" + picked.size + ")" : "Select an area first"}
        </button>
        {warn && (
          <div className="alert watch" style={{ marginTop: 12 }}>
            Severe pain deserves attention. If it is sudden, unusual for you, or comes with heavy bleeding, fever or
            fainting, please get medical care.
          </div>
        )}
      </div>

      <div className="section-title">Your pain history</div>
      {history.loading && <Loading />}
      <ErrorBox error={history.error} onRetry={history.reload} />
      {history.data && !pain.length && <div className="card empty muted">No body-map pain logged yet.</div>}
      {pain.length > 0 && (
        <>
          <div className="card">
            <Bars rows={summary} colorFor={(r) => `hsl(345, 42%, ${82 - r.avg * 8}%)`} />
            <p className="small muted" style={{ marginBottom: 0 }}>Darker bars mean stronger average pain.</p>
          </div>
          <div className="card menu">
            {pain.slice(0, 10).map((s) => (
              <div className="menu-row" key={s.id}>
                <span>{titleCase(s.symptom.slice(7))}</span>
                <span className="small muted" style={{ marginLeft: "auto" }}>{fmtDate(s.date)} · {s.severity}/5</span>
              </div>
            ))}
          </div>
        </>
      )}
    </Screen>
  );
}
