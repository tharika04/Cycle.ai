import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Icon from "../components/Icon.jsx";
import { Screen, TopBar } from "../components/ui.jsx";

const STEPS = [
  { label: "Breathe in", secs: 4, scale: 1.8 },
  { label: "Hold", secs: 4, scale: 1.8 },
  { label: "Breathe out", secs: 6, scale: 1 },
];

const TIPS = [
  { t: "Move a little", d: "A 10-minute walk or gentle stretch can calm a busy mind." },
  { t: "Write it down", d: "Journaling for a few minutes helps you notice what is weighing on you." },
  { t: "Protect your sleep", d: "Stress often feels bigger when you are tired, especially before your period." },
  { t: "Talk to someone", d: "A friend, family member, or counsellor can help. You don't have to manage alone." },
];

export default function Stress() {
  const [on, setOn] = useState(false);
  const [idx, setIdx] = useState(0);
  const [left, setLeft] = useState(STEPS[0].secs);
  const [rounds, setRounds] = useState(0);

  useEffect(() => {
    if (!on) return;
    const t = setTimeout(() => {
      if (left > 1) return setLeft(left - 1);
      const next = (idx + 1) % STEPS.length;
      if (next === 0) setRounds((r) => r + 1);
      setIdx(next);
      setLeft(STEPS[next].secs);
    }, 1000);
    return () => clearTimeout(t);
  }, [on, left, idx]);

  const toggle = () => {
    if (on) {
      setOn(false);
      setIdx(0);
      setLeft(STEPS[0].secs);
    } else {
      setOn(true);
      setRounds(0);
    }
  };

  const step = STEPS[idx];
  return (
    <Screen>
      <TopBar title="Manage Stress" subtitle="Slow your breathing, calm your body" />
      <div className="card center">
        <div className="breath">
          <div className="ring" />
          <div
            className="orb"
            style={{
              transform: `scale(${on ? step.scale : 1})`,
              transitionDuration: on ? step.secs + "s" : "0.4s",
            }}
          />
          <div className="lbl">{on ? step.label : "Ready?"}<br />{on ? left : ""}</div>
        </div>
        <p className="small muted" style={{ marginTop: 0 }}>In for 4 · hold for 4 · out for 6{rounds ? " · " + rounds + " round" + (rounds > 1 ? "s" : "") : ""}</p>
        <button className="btn" onClick={toggle}>
          <Icon name={on ? "pause" : "play"} size={18} fill={on ? "none" : "currentColor"} /> {on ? "Stop" : "Start breathing"}
        </button>
      </div>

      <div className="section-title">Quick ways to unwind</div>
      {TIPS.map((x) => (
        <div className="card" key={x.t}>
          <div style={{ fontWeight: 700, color: "var(--plum)" }}>{x.t}</div>
          <div className="small muted" style={{ marginTop: 2 }}>{x.d}</div>
        </div>
      ))}
      <Link to="/chat" className="btn ghost block" style={{ marginTop: 16 }}>
        <Icon name="chat" size={18} /> Talk it through with HerBot
      </Link>
      <p className="small muted center" style={{ marginTop: 14 }}>
        If you feel overwhelmed or unsafe, please reach out to a doctor or a local helpline.
      </p>
    </Screen>
  );
}
