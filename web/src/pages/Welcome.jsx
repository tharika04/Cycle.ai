import { Link, useNavigate } from "react-router-dom";
import { ART } from "../assets/art/index.js";
import { Flowers } from "../components/ui.jsx";
import Icon from "../components/Icon.jsx";

const FEATURES = [
  { icon: "calendar", text: "Track your periods" },
  { icon: "spark", text: "Get personalised insights" },
  { icon: "chat", text: "Chat with HerBot, our AI assistant" },
  { icon: "leaf", text: "Explore self-care tips" },
];

// Screen 2: welcome / get started. Leads to the login page.
export default function Welcome() {
  const navigate = useNavigate();
  return (
    <div className="welcome fade-in">
      <Flowers />
      <div className="dots"><i className="on" /><i /><i /><i /></div>
      <h1>
        Welcome to
        <br />
        HerRhythm ✨
      </h1>
      <p className="lead">Track your cycle, understand your body and take better care of yourself.</p>
      <img className="art-img float-slow glow" src={ART.calendar} alt="" style={{ width: "100%", maxWidth: 290, margin: "14px auto 10px" }} />
      <div>
        {FEATURES.map((f) => (
          <div className="feature" key={f.text}>
            <span className="ic"><Icon name={f.icon} size={18} /></span>
            {f.text}
          </div>
        ))}
      </div>
      <div style={{ marginTop: "auto", paddingTop: 24 }}>
        <button className="btn block" onClick={() => navigate("/login?mode=register")}>
          Get Started <Icon name="arrow" size={18} />
        </button>
        <p className="small" style={{ marginTop: 14 }}>
          Already have an account? <Link className="link" to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
