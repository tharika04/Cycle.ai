import { useEffect, useState } from "react";
import { api } from "../api.js";
import { ErrorBox, Loading, Screen, TopBar, useAsync } from "../components/ui.jsx";
import { titleCase } from "../cycle.js";

const PHASES = ["menstrual", "follicular", "ovulation", "luteal"];
const DIETS = ["vegetarian", "non-vegetarian", "vegan"];

function List({ title, items }) {
  return (
    <div className="card">
      <div style={{ fontWeight: 700, color: "var(--plum)", marginBottom: 6 }}>{title}</div>
      <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.65, fontSize: "0.9rem" }}>
        {items.map((x) => <li key={x}>{x}</li>)}
      </ul>
    </div>
  );
}

export default function Diet() {
  const pred = useAsync(() => api.predict().catch(() => null));
  const current = pred.data?.status === "ok" ? (pred.data.current_phase === "late" ? "luteal" : pred.data.current_phase) : null;
  const [phase, setPhase] = useState(null);
  const [diet, setDiet] = useState(() => {
    try { return localStorage.getItem("hr_diet") || "vegetarian"; } catch { return "vegetarian"; }
  });

  useEffect(() => {
    if (!pred.loading && phase === null) setPhase(current || "follicular");
  }, [pred.loading, current, phase]);

  const plan = useAsync(() => (phase ? api.plan(phase, diet) : Promise.resolve(null)), [phase, diet]);

  const pickDiet = (d) => {
    setDiet(d);
    try { localStorage.setItem("hr_diet", d); } catch { /* ignore */ }
  };

  const p = plan.data;
  return (
    <Screen>
      <TopBar title="Exercise & Food" subtitle={current ? "Your current phase: " + titleCase(current) : "Plans for each cycle phase"} />
      <div className="field">
        <span>Cycle phase</span>
        <div className="chips">
          {PHASES.map((x) => (
            <button key={x} className={"chip" + (phase === x ? " on" : "")} onClick={() => setPhase(x)}>
              {titleCase(x)}{x === current ? " •" : ""}
            </button>
          ))}
        </div>
      </div>
      <div className="field">
        <span>Diet preference</span>
        <div className="seg">
          {DIETS.map((d) => (
            <button key={d} className={diet === d ? "on" : ""} onClick={() => pickDiet(d)}>{titleCase(d)}</button>
          ))}
        </div>
      </div>

      {(plan.loading || pred.loading) && <Loading />}
      <ErrorBox error={plan.error} onRetry={plan.reload} />
      {p && !plan.loading && (
        <div className="stack">
          <div className="card" style={{ background: "var(--grad)", color: "#fff" }}>
            <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>{p.title}</div>
            <div style={{ fontSize: "0.9rem", marginTop: 4, opacity: 0.95 }}>{p.focus}</div>
          </div>
          <List title="🥗 What to eat" items={p.eat} />
          <List title="🚫 Go easy on" items={p.limit} />
          <div className="card">
            <div style={{ fontWeight: 700, color: "var(--plum)", marginBottom: 6 }}>🏃‍♀️ Exercise</div>
            <div className="grid-2" style={{ marginBottom: 8 }}>
              <div className="stat card" style={{ boxShadow: "none" }}><div className="v" style={{ fontSize: "0.95rem" }}>{p.exercise.intensity}</div><div className="l">Intensity</div></div>
              <div className="stat card" style={{ boxShadow: "none" }}><div className="v" style={{ fontSize: "0.85rem" }}>{p.exercise.duration}</div><div className="l">Duration</div></div>
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.65, fontSize: "0.9rem" }}>
              {p.exercise.activities.map((x) => <li key={x}>{x}</li>)}
            </ul>
          </div>
          <List title="💡 Tips" items={p.tips} />
          <p className="small muted center">{p.disclaimer}</p>
        </div>
      )}
    </Screen>
  );
}
