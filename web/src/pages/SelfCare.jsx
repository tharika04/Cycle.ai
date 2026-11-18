import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ART } from "../assets/art/index.js";
import Icon from "../components/Icon.jsx";
import { Screen } from "../components/ui.jsx";

// Layout from the client's Self-Care mockup, in the luxury style.
const CARDS = [
  { to: "/diet", name: "Exercise & Food", img: ART.careFood, meta: "Plans for your phase" },
  { to: "/health-check", name: "Health Check", img: ART.careHealth, meta: "Screen your cycle" },
  { to: "/routines", name: "Relax & Meditate", img: ART.careRelax, meta: "Cramp-relief routines" },
  { to: "/stress", name: "Manage Stress", img: ART.careStress, meta: "Guided breathing" },
];

const TIPS = [
  "Drink plenty of water to reduce cramps.",
  "A warm heat pad on your lower belly can ease period pain.",
  "Gentle stretching or a short walk can lift your mood.",
  "Iron-rich foods like spinach, dates and lentils help during your period.",
  "Aim for 7–9 hours of sleep, especially in the days before your period.",
  "Cut back on salty snacks to reduce bloating.",
];

export function CareCard({ to, name, img, meta }) {
  return (
    <Link to={to} className="card care-card shine">
      <img className="art-img" src={img} alt="" />
      <div className="name">{name}</div>
      {meta && <div className="meta">{meta}</div>}
      <span className="view">View <Icon name="arrow" size={13} /></span>
    </Link>
  );
}

export function WellnessTip() {
  const [i, setI] = useState(() => new Date().getDate() % TIPS.length);
  useEffect(() => {
    const t = setInterval(() => setI((x) => (x + 1) % TIPS.length), 6000);
    return () => clearInterval(t);
  }, []);
  return (
    <>
      <div className="section-title">Wellness Tips</div>
      <button className="card tip-card" style={{ width: "100%", textAlign: "left" }}
        onClick={() => setI((x) => (x + 1) % TIPS.length)} aria-label="Next tip">
        <img className="art-img float-slow" src={ART.tea} alt="" />
        <div key={i} className="fade-in" style={{ fontFamily: "var(--serif)", fontSize: "1.15rem", lineHeight: 1.35, fontWeight: 600, color: "var(--plum)" }}>
          {TIPS[i]}
        </div>
      </button>
      <div className="dots" style={{ marginTop: 10 }}>
        {TIPS.map((_, k) => <i key={k} className={k === i ? "on" : ""} />)}
      </div>
    </>
  );
}

export default function SelfCare() {
  return (
    <Screen>
      <div className="topbar">
        <img className="peony-badge" src={ART.peony} alt="" />
        <div className="grow">
          <h1 className="title">Self-Care</h1>
          <div className="subtitle">Small steps. Big difference.</div>
        </div>
      </div>
      <div className="grid-2">
        {CARDS.map((c) => <CareCard key={c.name} {...c} />)}
      </div>
      <WellnessTip />
    </Screen>
  );
}
