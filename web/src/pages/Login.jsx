import { useState } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../App.jsx";
import { ART } from "../assets/art/index.js";
import { Flowers } from "../components/ui.jsx";
import Icon from "../components/Icon.jsx";

// Screen 3: log in / create account.
export default function Login() {
  const [params] = useSearchParams();
  const [mode, setMode] = useState(params.get("mode") === "register" ? "register" : "login");
  const [form, setForm] = useState({ name: "", age: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const { token, login } = useAuth();
  const navigate = useNavigate();

  if (token) return <Navigate to="/home" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setNote("");
    setBusy(true);
    try {
      if (mode === "register") {
        await api.register({
          name: form.name.trim(),
          age: form.age ? Number(form.age) : null,
          email: form.email.trim(),
          password: form.password,
        });
      }
      await login(form.email.trim(), form.password);
      navigate("/home", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth page">
      {/* painted peony arrangement framing the form */}
      <Flowers strong />
      <img className="corner-art float-slow" src={ART.peony} alt="" style={{ width: 70, top: 200, left: 6, opacity: 0.9 }} />
      <img className="corner-art float-slow" src={ART.peony} alt="" style={{ width: 54, bottom: 140, right: 18, opacity: 0.85, animationDelay: "1.4s" }} />
      <button className="icon-btn" onClick={() => navigate("/welcome")} aria-label="Back">
        <Icon name="back" />
      </button>
      <div className="auth-head">
        <img className="lotus-img heartbeat" style={{ animationDuration: "3.2s" }} src={ART.lotus} alt="HerRhythm logo" />
        <div className="brand">HerRhythm</div>
        <div className="subtitle">
          {mode === "login" ? "Welcome back! Log in to continue." : "Create your account to get started."}
        </div>
      </div>

      <div className="seg" style={{ marginBottom: 18 }}>
        <button className={mode === "login" ? "on" : ""} onClick={() => setMode("login")} type="button">Log in</button>
        <button className={mode === "register" ? "on" : ""} onClick={() => setMode("register")} type="button">Sign up</button>
      </div>

      <form className="card" onSubmit={submit} style={{ padding: 20 }}>
        {mode === "register" && (
          <>
            <label className="field">
              <span>Name</span>
              <input className="input" required value={form.name} onChange={set("name")} autoComplete="name" placeholder="Your name" />
            </label>
            <label className="field">
              <span>Age</span>
              <input className="input" type="number" min="10" max="100" value={form.age} onChange={set("age")} placeholder="Optional" />
            </label>
          </>
        )}
        <label className="field">
          <span>Email</span>
          <input className="input" type="email" required value={form.email} onChange={set("email")} autoComplete="email" placeholder="you@example.com" />
        </label>
        <label className="field">
          <span>Password</span>
          <input
            className="input"
            type="password"
            required
            minLength={mode === "register" ? 6 : undefined}
            value={form.password}
            onChange={set("password")}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            placeholder={mode === "register" ? "At least 6 characters" : "Your password"}
          />
        </label>
        {error && <div className="alert danger" style={{ marginBottom: 14 }}>{error}</div>}
        {note && <div className="alert ok" style={{ marginBottom: 14 }}>{note}</div>}
        <button className="btn block" disabled={busy}>
          {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
        </button>
      </form>

      <p className="center small muted" style={{ marginTop: 16 }}>
        {mode === "login" ? "New to HerRhythm? " : "Already have an account? "}
        <button className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Create an account" : "Log in"}
        </button>
      </p>
    </div>
  );
}
