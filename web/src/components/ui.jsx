import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import Icon from "./Icon.jsx";
import { FallingPetals } from "./Art.jsx";
import { ART } from "../assets/art/index.js";

/** Scroll offset, throttled to animation frames (for parallax layers). */
function useScrollY() {
  const [y, setY] = useState(0);
  useEffect(() => {
    let raf = 0;
    const on = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => setY(window.scrollY));
    };
    window.addEventListener("scroll", on, { passive: true });
    return () => {
      window.removeEventListener("scroll", on);
      cancelAnimationFrame(raf);
    };
  }, []);
  return y;
}

/** Painted flower corners (with parallax), a blossom branch and drifting petals behind a screen. */
export function Flowers({ petals = true, strong = false }) {
  const y = useScrollY();
  return (
    <>
      <div className="corner-art tr" style={{ top: -18, right: -26, width: strong ? 230 : 170, opacity: strong ? 0.95 : 0.6,
        transform: `translateY(${y * 0.35}px) scaleX(-1)` }}>
        <img src={ART.corner} alt="" />
      </div>
      <div className="corner-art" style={{ bottom: 70, left: -34, width: strong ? 220 : 150, opacity: strong ? 0.9 : 0.5,
        transform: `translateY(${-y * 0.15}px) rotate(180deg) scaleX(-1)` }}>
        <img src={ART.corner} alt="" />
      </div>
      <div className="corner-art" style={{ top: 330, right: -40, width: 90, opacity: 0.35, transform: `translateY(${y * 0.2}px)` }}>
        <img src={ART.branch} alt="" />
      </div>
      {petals && <FallingPetals count={6} />}
    </>
  );
}

/** Petal burst from the middle of the screen, for happy moments like saving a log. */
export function celebrate() {
  const root = document.createElement("div");
  root.className = "burst";
  const colors = ["#f2c7bd", "#dc96a6", "#c86d84", "#e6c2b3", "#f5d9df", "#b9806f"];
  for (let i = 0; i < 26; i++) {
    const p = document.createElement("i");
    const angle = (Math.PI * 2 * i) / 26 + Math.random() * 0.4;
    const dist = 110 + Math.random() * 120;
    p.style.setProperty("--x", Math.cos(angle) * dist + "px");
    p.style.setProperty("--y", Math.sin(angle) * dist + 60 + "px");
    p.style.setProperty("--r", Math.round(Math.random() * 540 - 270) + "deg");
    p.style.background = colors[i % colors.length];
    p.style.animationDelay = Math.random() * 0.12 + "s";
    root.appendChild(p);
  }
  document.body.appendChild(root);
  setTimeout(() => root.remove(), 1600);
}

/** Animated number that counts up to its value. */
export function CountUp({ value, duration = 900 }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const target = Number(value) || 0;
    let raf;
    const start = performance.now();
    const tick = (t) => {
      const k = Math.min(1, (t - start) / duration);
      setN(Math.round(target * (1 - Math.pow(1 - k, 3))));
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);
  return n;
}

/* ---------- data loading ---------- */
export function useAsync(fn, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const [tick, setTick] = useState(0);
  const fnRef = useRef(fn);
  fnRef.current = fn;
  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fnRef
      .current()
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);
  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { ...state, reload };
}

/* ---------- toast ---------- */
const ToastCtx = createContext(() => {});
export function ToastProvider({ children }) {
  const [msg, setMsg] = useState(null);
  const timer = useRef();
  const show = useCallback((text) => {
    setMsg(text);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setMsg(null), 2600);
  }, []);
  return (
    <ToastCtx.Provider value={show}>
      {children}
      {msg && <div className="toast" role="status">{msg}</div>}
    </ToastCtx.Provider>
  );
}
export const useToast = () => useContext(ToastCtx);

/* ---------- layout ---------- */
export function Screen({ children, nav = true, decor = true, className = "" }) {
  return (
    <div className={"screen page " + (nav ? "" : "no-nav ") + className}>
      {decor && <Flowers />}
      {children}
    </div>
  );
}

export function TopBar({ title, subtitle, back = true, right }) {
  const navigate = useNavigate();
  return (
    <div className="topbar">
      {back && (
        <button className="icon-btn" onClick={() => navigate(-1)} aria-label="Back">
          <Icon name="back" />
        </button>
      )}
      <div className="grow">
        <h1 className="title">{title}</h1>
        {subtitle && <div className="subtitle">{subtitle}</div>}
      </div>
      {right}
    </div>
  );
}

export function BottomNav() {
  const items = [
    { to: "/home", label: "Home", icon: "home" },
    { to: "/calendar", label: "Calendar", icon: "calendar" },
    { to: "/track", label: "Track", icon: "plus", plus: true },
    { to: "/chat", label: "HerBot", icon: "chat" },
    { to: "/profile", label: "Profile", icon: "user" },
  ];
  return (
    <nav className="bottom-nav" aria-label="Main">
      {items.map((it) =>
        it.plus ? (
          <NavLink key={it.to} to={it.to} aria-label="Track">
            <span className="plus">
              <Icon name="plus" size={26} stroke={2.6} />
            </span>
          </NavLink>
        ) : (
          <NavLink key={it.to} to={it.to} className={({ isActive }) => (isActive ? "active" : "")}>
            <Icon name={it.icon} size={22} />
            {it.label}
          </NavLink>
        )
      )}
    </nav>
  );
}

export function Loading() {
  return <div className="spinner" aria-label="Loading" />;
}

export function ErrorBox({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="alert danger">
      <b>Something went wrong</b>
      {error.message || String(error)}
      {onRetry && (
        <div style={{ marginTop: 8 }}>
          <button className="btn sm ghost" onClick={onRetry}>Try again</button>
        </div>
      )}
    </div>
  );
}

export function Sheet({ open, onClose, children }) {
  if (!open) return null;
  return (
    <>
      <div className="sheet-backdrop" onClick={onClose} />
      <div className="sheet" role="dialog" aria-modal="true">
        <div className="grab" />
        {children}
      </div>
    </>
  );
}

export function Bars({ rows, max, colorFor }) {
  const top = max ?? Math.max(1, ...rows.map((r) => r.value));
  return (
    <div>
      {rows.map((r) => (
        <div className="bar-row" key={r.label}>
          <span className="lbl" title={r.label}>{r.label}</span>
          <span className="track">
            {(r.parts || [{ value: r.value, color: colorFor ? colorFor(r) : "var(--pink-500)" }]).map((p, i) => (
              <i key={i} style={{ width: (100 * p.value) / top + "%", background: p.color }} title={p.title} />
            ))}
          </span>
          <span className="n">{r.display ?? r.value}</span>
        </div>
      ))}
    </div>
  );
}
