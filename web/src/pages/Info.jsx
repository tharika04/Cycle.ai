import { Link } from "react-router-dom";
import { Lotus } from "../components/Art.jsx";
import { Screen, TopBar } from "../components/ui.jsx";

export function About() {
  return (
    <Screen>
      <TopBar title="About HerRhythm" />
      <div className="card center">
        <div style={{ display: "flex", justifyContent: "center" }}><Lotus size={90} /></div>
        <div className="brand" style={{ fontSize: "1.8rem", marginTop: 6 }}>HerRhythm</div>
        <div className="subtitle">Track • Understand • Thrive</div>
        <p style={{ lineHeight: 1.6, fontSize: "0.92rem" }}>
          HerRhythm is your personal menstrual and wellness companion. It predicts your next period and fertile
          window, helps you spot symptom patterns, suggests food and movement for each cycle phase, and answers
          your questions with an AI assistant.
        </p>
      </div>
      <div className="alert info" style={{ marginTop: 12 }}>
        HerRhythm gives general information only. Predictions are estimates and must not be used as
        contraception. It does not replace advice from a doctor.
      </div>
    </Screen>
  );
}

const FAQ = [
  ["How are predictions made?", "From the dates you log. Recent cycles count more. Log at least 3 periods for better accuracy."],
  ["How do I log symptoms?", "Tap + at the bottom, then 'Symptoms & more'. Or tap any past date on the Calendar."],
  ["How do I fix a wrong period date?", "Go to Track → Period. Delete the wrong entry from Cycle history and add it again."],
  ["Can I change HerBot's language?", "Yes. Open HerBot and tap the menu button at the top right."],
  ["How do I share data with my doctor?", "Profile → Health Reports → Download PDF report."],
];

export function Help() {
  return (
    <Screen>
      <TopBar title="Help & Support" />
      {FAQ.map(([q, a]) => (
        <div className="card" key={q}>
          <div style={{ fontWeight: 700, color: "var(--plum)" }}>{q}</div>
          <div className="small muted" style={{ marginTop: 4, lineHeight: 1.5 }}>{a}</div>
        </div>
      ))}
      <Link to="/chat" className="btn block" style={{ marginTop: 16 }}>Ask HerBot a question</Link>
    </Screen>
  );
}
