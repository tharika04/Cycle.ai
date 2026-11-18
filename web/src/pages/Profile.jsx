import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../App.jsx";
import { ART } from "../assets/art/index.js";
import Icon from "../components/Icon.jsx";
import { Screen } from "../components/ui.jsx";

const ROWS = [
  { icon: "history", label: "Cycle History", to: "/track?tab=period" },
  { icon: "report", label: "Health Reports", to: "/insights" },
  { icon: "bell", label: "Notifications", to: "/reminders" },
  { icon: "lock", label: "Privacy & Security", to: "/settings" },
  { icon: "info", label: "About HerRhythm", to: "/about" },
  { icon: "help", label: "Help & Support", to: "/help" },
];

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const name = user?.name || "";

  return (
    <Screen>
      <div className="row between">
        <span />
        <Link to="/settings" className="icon-btn" aria-label="Settings"><Icon name="gear" size={22} /></Link>
      </div>
      <div className="profile-head">
        <div className="avatar-halo">
          <div className="avatar">{(name[0] || "H").toUpperCase()}</div>
          <img className="peony-badge" src={ART.peony} alt="" style={{ position: "absolute", right: -18, bottom: -6, width: 50, height: 50 }} />
          <img className="peony-badge" src={ART.peony} alt="" style={{ position: "absolute", left: -14, top: -8, width: 34, height: 34, animationDelay: "1.5s", transform: "scaleX(-1)" }} />
        </div>
        <h2>{name || "Your profile"}</h2>
        <div className="subtitle">{user?.email}</div>
      </div>

      <div className="card menu">
        {ROWS.map((r) => (
          <button key={r.label} className="menu-row" onClick={() => navigate(r.to)}>
            <span className="ic"><Icon name={r.icon} /></span>
            {r.label}
            <Icon name="chevron" size={18} className="chev" />
          </button>
        ))}
        <button className="menu-row" onClick={logout}>
          <span className="ic"><Icon name="logout" /></span>
          Log Out
          <Icon name="chevron" size={18} className="chev" />
        </button>
      </div>
    </Screen>
  );
}
