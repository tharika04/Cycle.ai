import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { HashRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api.js";
import { BottomNav, ToastProvider } from "./components/ui.jsx";

import Splash from "./pages/Splash.jsx";
import Welcome from "./pages/Welcome.jsx";
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";
import CalendarPage from "./pages/Calendar.jsx";
import Track from "./pages/Track.jsx";
import Chat from "./pages/Chat.jsx";
import Profile from "./pages/Profile.jsx";
import SelfCare from "./pages/SelfCare.jsx";
import Routines, { RoutineDetail } from "./pages/Routines.jsx";
import Stress from "./pages/Stress.jsx";
import Diet from "./pages/Diet.jsx";
import HealthCheck from "./pages/HealthCheck.jsx";
import Insights from "./pages/Insights.jsx";
import Reminders from "./pages/Reminders.jsx";
import Settings from "./pages/Settings.jsx";
import BodyMap from "./pages/BodyMap.jsx";
import { About, Help } from "./pages/Info.jsx";

/* ---------- auth ---------- */
const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

function AuthProvider({ children }) {
  const [token, setTok] = useState(getToken());
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const logout = useCallback(() => {
    setToken(null);
    setTok(null);
    setUser(null);
    navigate("/login", { replace: true });
  }, [navigate]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setTok(null);
      setUser(null);
      navigate("/login", { replace: true });
    });
  }, [navigate]);

  useEffect(() => {
    if (!token) return;
    api.me().then(setUser).catch(() => {});
  }, [token]);

  const login = useCallback(async (email, password) => {
    const t = await api.login(email, password);
    setToken(t);
    setTok(t);
  }, []);

  return <AuthCtx.Provider value={{ token, user, login, logout }}>{children}</AuthCtx.Provider>;
}

function Private({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

const NAV_ROUTES = ["/home", "/calendar", "/track", "/chat", "/profile", "/self-care", "/routines", "/stress",
  "/diet", "/health-check", "/insights", "/reminders", "/settings", "/body-map", "/about", "/help"];

function Shell() {
  const location = useLocation();
  const { token } = useAuth();
  const showNav = token && NAV_ROUTES.some((r) => location.pathname.startsWith(r));
  const p = (el) => <Private>{el}</Private>;

  // scroll to top on page change
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/welcome" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/home" element={p(<Home />)} />
        <Route path="/calendar" element={p(<CalendarPage />)} />
        <Route path="/track" element={p(<Track />)} />
        <Route path="/chat" element={p(<Chat />)} />
        <Route path="/profile" element={p(<Profile />)} />
        <Route path="/self-care" element={p(<SelfCare />)} />
        <Route path="/routines" element={p(<Routines />)} />
        <Route path="/routines/:key" element={p(<RoutineDetail />)} />
        <Route path="/stress" element={p(<Stress />)} />
        <Route path="/diet" element={p(<Diet />)} />
        <Route path="/health-check" element={p(<HealthCheck />)} />
        <Route path="/insights" element={p(<Insights />)} />
        <Route path="/reminders" element={p(<Reminders />)} />
        <Route path="/settings" element={p(<Settings />)} />
        <Route path="/body-map" element={p(<BodyMap />)} />
        <Route path="/about" element={p(<About />)} />
        <Route path="/help" element={p(<Help />)} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      {showNav && <BottomNav />}
    </div>
  );
}

export default function App() {
  return (
    <HashRouter>
      <ToastProvider>
        <AuthProvider>
          <Shell />
        </AuthProvider>
      </ToastProvider>
    </HashRouter>
  );
}
