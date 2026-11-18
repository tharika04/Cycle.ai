import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { Legend } from "../components/CycleWheel.jsx";
import Icon from "../components/Icon.jsx";
import { ErrorBox, Loading, Screen, TopBar, useAsync, useToast } from "../components/ui.jsx";
import { MARK_STYLE, MONTHS, PHASE_TIPS, WEEKDAYS, buildMarks, dayClass, monthWeeks, titleCase, toISO, today } from "../cycle.js";

function MonthGrid({ year, month, marks, logged, onPick, mini = false }) {
  const now = toISO(today());
  return (
    <div className={"card month" + (mini ? " mini" : "")}>
      {mini && <h4>{MONTHS[month].slice(0, 3)}</h4>}
      <div className="cal-grid">
        {WEEKDAYS.map((w, i) => (
          <div className="cal-wd" key={i}>{w}</div>
        ))}
        {monthWeeks(year, month).flat().map((d, i) => {
          if (!d) return <div key={i} />;
          const iso = toISO(new Date(year, month, d));
          const st = MARK_STYLE[dayClass(iso, marks)];
          const cls = ["cal-day", iso === now && "today", iso > now && "future", !mini && logged.has(iso) && "dot"]
            .filter(Boolean)
            .join(" ");
          const style = st ? { background: st.bg, color: st.fg, fontWeight: 600 } : undefined;
          return mini ? (
            <div key={i} className={cls} style={style}>{d}</div>
          ) : (
            <button key={i} className={cls} style={style} onClick={() => onPick(iso)} aria-label={iso}>
              {d}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function CalendarPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [view, setView] = useState("month");
  const [cursor, setCursor] = useState(() => {
    const t = today();
    return { y: t.getFullYear(), m: t.getMonth() };
  });
  const { data, error, loading, reload } = useAsync(() =>
    Promise.all([api.predict(), api.cycles(), api.loggedDates().catch(() => [])])
  );
  const [pred, cycles, loggedList] = data || [];
  const marks = useMemo(() => buildMarks(cycles, pred), [cycles, pred]);
  const logged = useMemo(() => new Set(loggedList || []), [loggedList]);
  const ok = pred?.status === "ok";

  const shift = (n) =>
    setCursor(({ y, m }) => {
      const t = y * 12 + m + n;
      return { y: Math.floor(t / 12), m: ((t % 12) + 12) % 12 };
    });

  const pick = (iso) => {
    if (iso > toISO(today())) return toast("You can only log today or earlier days.");
    navigate("/track?tab=day&date=" + iso);
  };

  return (
    <Screen>
      <TopBar title="Calendar" back={false} right={<Link to="/track?tab=period" className="icon-btn" aria-label="Edit periods"><Icon name="edit" /></Link>} />
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && !ok && (
        <div className="card empty">
          <p>Log your first period to see your calendar.</p>
          <Link className="btn" to="/track?tab=period">Log your last period</Link>
        </div>
      )}
      {data && ok && (
        <>
          <div className="grid-3">
            <div className="card stat"><div className="v">{titleCase(pred.current_phase)}</div><div className="l">Phase</div></div>
            <div className="card stat"><div className="v">{pred.day_in_cycle}</div><div className="l">Day of cycle</div></div>
            <div className="card stat">
              <div className="v">{pred.days_until_next_period >= 0 ? pred.days_until_next_period + "d" : -pred.days_until_next_period + "d late"}</div>
              <div className="l">Next period</div>
            </div>
          </div>
          <div className="alert info" style={{ marginTop: 12 }}>{PHASE_TIPS[pred.current_phase]}</div>

          <div className="seg" style={{ margin: "16px 0 6px" }}>
            <button className={view === "month" ? "on" : ""} onClick={() => setView("month")}>Month</button>
            <button className={view === "year" ? "on" : ""} onClick={() => setView("year")}>Year</button>
          </div>
          <Legend />

          {view === "month" ? (
            <>
              <div className="month-head" style={{ margin: "14px 4px 8px" }}>
                <button className="icon-btn" onClick={() => shift(-1)} aria-label="Previous month"><Icon name="left" /></button>
                <h3>{MONTHS[cursor.m]} {cursor.y}</h3>
                <button className="icon-btn" onClick={() => shift(1)} aria-label="Next month"><Icon name="right" /></button>
              </div>
              <MonthGrid year={cursor.y} month={cursor.m} marks={marks} logged={logged} onPick={pick} />
              <p className="center small muted" style={{ marginTop: 10 }}>
                Tap a date to log how you feel. A purple dot means something is logged.
              </p>
            </>
          ) : (
            <>
              <div className="month-head" style={{ margin: "14px 4px 8px" }}>
                <button className="icon-btn" onClick={() => shift(-12)} aria-label="Previous year"><Icon name="left" /></button>
                <h3>{cursor.y}</h3>
                <button className="icon-btn" onClick={() => shift(12)} aria-label="Next year"><Icon name="right" /></button>
              </div>
              <div className="grid-3" style={{ gap: 8 }}>
                {MONTHS.map((_, m) => (
                  <MonthGrid key={m} year={cursor.y} month={m} marks={marks} logged={logged} mini />
                ))}
              </div>
            </>
          )}

          {pred.confidence === "low" && (
            <p className="small muted center" style={{ marginTop: 12 }}>Confidence is low. Log at least 3 cycles for better predictions.</p>
          )}
          {pred.irregular && (
            <div className="alert watch" style={{ marginTop: 12 }}>
              Your cycles look irregular. Consider talking to a doctor if this continues.
            </div>
          )}
          <p className="small muted center" style={{ marginTop: 12 }}>{pred.note}</p>
        </>
      )}
    </Screen>
  );
}
