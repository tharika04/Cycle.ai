import { Link } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../App.jsx";
import CycleWheel, { Legend } from "../components/CycleWheel.jsx";
import Icon from "../components/Icon.jsx";
import { CountUp, ErrorBox, Loading, Screen, useAsync } from "../components/ui.jsx";
import { PHASE_TIPS, addDays, buildMarks, fmtDate, toISO, today } from "../cycle.js";

const SYM_EMOJI = {
  cramps: "🩸", headache: "🤕", "back pain": "🦴", fatigue: "🥱", bloating: "🎈", acne: "🔴",
  "breast tenderness": "💗", cravings: "🍫", insomnia: "🌙", nausea: "🤢", "mood swings": "🎭",
  "abdominal pain": "😣", "hot flashes": "🔥", "night sweats": "💦", "joint pain": "🦵",
};
const LEVELS = [
  { max: 2.4, label: "Mild", color: "#f3cdd6" },
  { max: 3.6, label: "Moderate", color: "#dc96a6" },
  { max: 9, label: "Strong", color: "#a94a67" },
];
const levelOf = (sev) => LEVELS.find((l) => sev <= l.max);
const niceName = (s) => (s.startsWith("pain - ") ? "Pain: " + s.slice(7) : s).replace(/^\w/, (c) => c.toUpperCase());

/** Simple chart: which symptoms were logged on how many days in the last 30 days, and how strong. */
function SymptomChart({ symptoms }) {
  const since = toISO(addDays(today(), -29));
  const map = {};
  (symptoms || []).filter((s) => s.date >= since).forEach((s) => {
    const m = (map[s.symptom] = map[s.symptom] || { days: new Set(), sev: [] });
    m.days.add(s.date);
    m.sev.push(s.severity);
  });
  const rows = Object.entries(map)
    .map(([name, m]) => ({ name, days: m.days.size, sev: m.sev.reduce((a, b) => a + b, 0) / m.sev.length }))
    .sort((a, b) => b.days - a.days || b.sev - a.sev)
    .slice(0, 5);
  const top = Math.max(1, ...rows.map((r) => r.days));

  return (
    <div className="card" style={{ marginTop: 14 }}>
      <div className="row between">
        <div>
          <div style={{ fontWeight: 700, color: "var(--plum)" }}>Your symptoms</div>
          <div className="small muted">Last 30 days</div>
        </div>
        <Link to="/track?tab=day" className="btn sm ghost"><Icon name="plus" size={14} /> Log</Link>
      </div>

      {rows.length === 0 ? (
        <p className="small muted" style={{ margin: "12px 0 0" }}>
          No symptoms logged in the last 30 days. Tap <b>Log</b> to add how you feel today.
        </p>
      ) : (
        <>
          <div className="alert info small" style={{ margin: "12px 0" }}>
            Most common: <b style={{ display: "inline" }}>{SYM_EMOJI[rows[0].name] || "•"} {niceName(rows[0].name)}</b> on{" "}
            {rows[0].days} day{rows[0].days > 1 ? "s" : ""}
          </div>
          {rows.map((r) => {
            const lv = levelOf(r.sev);
            return (
              <div key={r.name} style={{ marginBottom: 10 }}>
                <div className="row between small" style={{ marginBottom: 4 }}>
                  <span style={{ fontWeight: 600 }}>{SYM_EMOJI[r.name] || "•"} {niceName(r.name)}</span>
                  <span className="muted">{r.days} day{r.days > 1 ? "s" : ""} · {lv.label}</span>
                </div>
                <div className="progress" style={{ height: 12 }}>
                  <div style={{ width: (100 * r.days) / top + "%", background: lv.color }} />
                </div>
              </div>
            );
          })}
          <div className="legend" style={{ marginTop: 4 }}>
            {LEVELS.map((l) => <span key={l.label}><i style={{ background: l.color }} />{l.label}</span>)}
          </div>
        </>
      )}
    </div>
  );
}

export default function Home() {
  const { user } = useAuth();
  const { data, error, loading, reload } = useAsync(() =>
    Promise.all([api.predict(), api.cycles(), api.symptoms().catch(() => [])])
  );
  const [pred, cycles, symptoms] = data || [];
  const ok = pred?.status === "ok";
  const name = user?.name || "";

  const left = ok ? Number(pred.days_until_next_period) : null;
  const pct = ok ? Math.min(100, Math.round((100 * pred.day_in_cycle) / Math.max(pred.avg_cycle_length, 1))) : 0;

  return (
    <Screen>
      <div className="topbar">
        <div className="avatar">{(name[0] || "H").toUpperCase()}</div>
        <div className="grow">
          <h1 className="title" style={{ fontSize: "1.2rem" }}>Hello{name ? ", " + name : ""}! 👋</h1>
          <div className="subtitle">You're doing great!</div>
        </div>
        <Link to="/reminders" className="icon-btn" aria-label="Reminders"><Icon name="bell" /></Link>
      </div>

      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />

      {data && (
        <>
          <Link to={ok ? "/calendar" : "/track"} className="card next-card shine">
            <span className="ic"><Icon name="calendar" size={26} /></span>
            <div>
              {ok ? (
                <>
                  <div className="small muted">{left > 0 ? "Next period in" : "Next period"}</div>
                  <div className="big">{left > 0 ? <><CountUp value={left} /> days</> : left === 0 ? "Today" : <><CountUp value={-left} /> days late</>}</div>
                  <div className="small muted">Expected: {fmtDate(pred.next_period_start)}</div>
                </>
              ) : (
                <>
                  <div className="small muted">Next period</div>
                  <div className="big" style={{ fontSize: "1.2rem" }}>Add your last period</div>
                  <div className="small muted">Tap + to log it</div>
                </>
              )}
            </div>
          </Link>

          <div className="wheel-wrap">
            <CycleWheel pred={pred} marks={buildMarks(cycles, pred)} />
            <Legend />
          </div>

          {ok && (
            <div className="card" style={{ marginTop: 14 }}>
              <div className="row between small" style={{ fontWeight: 600, marginBottom: 8 }}>
                <span>Cycle progress</span>
                <span>{pct}%</span>
              </div>
              <div className="progress"><div style={{ width: pct + "%" }} /></div>
              {pred.confidence === "low" && (
                <div className="small muted" style={{ marginTop: 8 }}>
                  Confidence is low. Log at least 3 cycles for better predictions.
                </div>
              )}
            </div>
          )}

          <SymptomChart symptoms={symptoms} />

          <div className="grid-3" style={{ marginTop: 14 }}>
            <Link to="/self-care" className="card tile"><span className="ic"><Icon name="heart" /></span>Self-Care</Link>
            <Link to="/insights" className="card tile"><span className="ic"><Icon name="report" /></span>Reports</Link>
            <Link to="/body-map" className="card tile"><span className="ic"><Icon name="body" /></span>Body Map</Link>
          </div>

          <div className="card tip-card" style={{ marginTop: 14 }}>
            <span className="next-card"><span className="ic" style={{ background: "#fff3d6", color: "#c98a00" }}><Icon name="bulb" /></span></span>
            <div>
              <div style={{ fontWeight: 700, color: "var(--plum)" }}>Today's tip</div>
              <div className="small" style={{ lineHeight: 1.5 }}>
                {PHASE_TIPS[ok ? pred.current_phase : ""] || "Log your first period to get daily guidance."}
              </div>
            </div>
          </div>
          <p className="center small muted" style={{ marginTop: 14 }}>Estimates based on your logs, not medical advice.</p>
        </>
      )}
    </Screen>
  );
}
