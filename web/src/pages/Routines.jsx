import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { ART as IMG } from "../assets/art/index.js";
import Icon from "../components/Icon.jsx";
import { ErrorBox, Loading, Screen, TopBar, celebrate, useAsync } from "../components/ui.jsx";
import { CareCard, WellnessTip } from "./SelfCare.jsx";

const ART = { wake: IMG.rWake, back: IMG.rBack, body: IMG.rBody };
const meta = (r) => Math.round(r.total_seconds / 60 * 10) / 10 + " min · " + r.poses.length + " poses";

// Cramp relief: the three routines shown as cards in the style of the client's Self-Care mockup.
export default function Routines() {
  const { data, error, loading, reload } = useAsync(() => api.routines());
  return (
    <Screen>
      <TopBar title="Cramp Relief" subtitle="Gentle movement to ease cramps" />
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && (
        <div className="grid-2">
          {data.map((r) => (
            <CareCard key={r.key} to={"/routines/" + r.key} name={r.title} img={ART[r.key] || IMG.rBack} meta={meta(r)} />
          ))}
          <CareCard to="/stress" name="Breathing" img={IMG.rBreath} meta="4-4-6 breathing" />
        </div>
      )}
      <div className="alert info" style={{ marginTop: 16 }}>
        Stop if anything hurts, and see a doctor for severe or unusual pain.
      </div>
      <WellnessTip />
    </Screen>
  );
}

export function RoutineDetail() {
  const { key } = useParams();
  const { data, error, loading, reload } = useAsync(() => api.routines());
  const routine = data?.find((r) => r.key === key);
  const [step, setStep] = useState(null); // null = overview, number = guided pose index

  return (
    <Screen>
      <TopBar title={routine?.title || "Routine"} subtitle={routine ? meta(routine) : ""} />
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && !routine && <div className="card empty">Routine not found. <Link className="link" to="/routines">Back</Link></div>}
      {routine && step === null && (
        <>
          <button className="btn block" onClick={() => setStep(0)}><Icon name="play" size={18} fill="currentColor" /> Start guided routine</button>
          {routine.poses.map((p, i) => (
            <div className="card" key={i} style={{ marginTop: 14 }}>
              <img className="pose-fig" src={api.figureUrl(p.figure)} alt={p.name} loading="lazy" />
              <div style={{ fontWeight: 700, color: "var(--plum)", marginTop: 10 }}>{i + 1}. {p.name}</div>
              <div className="small muted">Hold {p.seconds} seconds · {p.tip}</div>
            </div>
          ))}
        </>
      )}
      {routine && step !== null && <Guided routine={routine} step={step} setStep={setStep} />}
    </Screen>
  );
}

function Guided({ routine, step, setStep }) {
  const count = routine.poses.length;
  const pose = routine.poses[step];
  const [left, setLeft] = useState(pose?.seconds ?? 0);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    setLeft(pose?.seconds ?? 0);
    setRunning(false);
  }, [step, pose?.seconds]);

  useEffect(() => {
    if (!running) return;
    if (left <= 0) {
      setRunning(false);
      return;
    }
    const t = setTimeout(() => setLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [running, left]);

  useEffect(() => {
    if (step >= count) celebrate();
  }, [step, count]);

  if (step >= count) {
    return (
      <div className="card empty">
        <h2 style={{ margin: "8px 0", fontFamily: "var(--serif)", fontSize: "2rem" }}>Well done!</h2>
        <p className="muted">You finished the routine. Drink some water and rest if you need to.</p>
        <button className="btn" onClick={() => setStep(null)}>Close</button>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="row between small" style={{ fontWeight: 600, marginBottom: 8 }}>
        <span>Pose {step + 1} of {count}</span>
        <span>{Math.round((100 * step) / count)}%</span>
      </div>
      <div className="progress" style={{ marginBottom: 14 }}><div style={{ width: (100 * step) / count + "%" }} /></div>
      <img className="pose-fig" src={api.figureUrl(pose.figure)} alt={pose.name} />
      <h2 className="center" style={{ margin: "12px 0 4px" }}>{pose.name}</h2>
      <p className="center small muted" style={{ margin: 0 }}>Tip: {pose.tip}</p>
      <div className="timer" style={{ margin: "12px 0" }}>{left > 0 ? left + "s" : "Done ✓"}</div>
      <div className="grid-3">
        <button className="btn ghost sm" disabled={step === 0} onClick={() => setStep(step - 1)}><Icon name="left" size={16} /> Back</button>
        <button className="btn sm" onClick={() => (left <= 0 ? setLeft(pose.seconds) : setRunning(!running))}>
          <Icon name={running ? "pause" : "timer"} size={16} /> {running ? "Pause" : left <= 0 ? "Again" : "Timer"}
        </button>
        <button className="btn ghost sm" onClick={() => setStep(step + 1)}>Next <Icon name="right" size={16} /></button>
      </div>
      <button className="btn outline block sm" style={{ marginTop: 12 }} onClick={() => setStep(null)}>End routine</button>
    </div>
  );
}
