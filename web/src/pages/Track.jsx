import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api.js";
import Icon from "../components/Icon.jsx";
import { ErrorBox, Loading, Screen, TopBar, celebrate, useAsync, useToast } from "../components/ui.jsx";
import { MONTHS, addDays, fmtDate, parseISO, toISO, today } from "../cycle.js";

const EMOJI = {
  Calm: "😌", Happy: "😊", Energetic: "⚡", Frisky: "😜", "Mood swings": "🎭", Irritated: "😠", Sad: "😢",
  Anxious: "😰", Depressed: "😞", "Feeling guilty": "😔", "Obsessive thoughts": "💭", "Low energy": "🔋",
  Apathetic: "😑", Confused: "😕", "Very self-critical": "😣",
  "Everything is fine": "👍", Cramps: "🩸", "Tender breasts": "💗", Headache: "🤕", Acne: "🔴", Backache: "🦴",
  Fatigue: "🥱", Cravings: "🍔", Insomnia: "🌙", "Abdominal pain": "😣", "Vaginal itching": "🔸",
  "Vaginal dryness": "🏜️", "Hot flashes": "🔥", "Night sweats": "💦", "Joint pain": "🦵",
  "No discharge": "🚫", Creamy: "🥛", Watery: "💧", Sticky: "🍯", "Egg white": "🥚", Spotting: "🩸",
  Unusual: "❓", "Clumpy white": "☁️", Gray: "🌫️",
  Nausea: "🤢", Bloating: "🎈", Constipation: "🧱", Diarrhea: "🚽",
  Travel: "✈️", Stress: "⚡", Meditation: "🧘", Journaling: "📓", "Kegel exercises": "💪",
  "Breathing exercises": "🌬️", "Disease or injury": "🩹", Alcohol: "🍷",
  "Didn't exercise": "🛋️", Yoga: "🧘‍♀️", Gym: "🏋️", "Aerobics & dancing": "💃", Swimming: "🏊",
  "Team sports": "🏀", Running: "🏃", Cycling: "🚴", Walking: "🚶",
};
const CAT_COLOR = {
  mood: "#d39a6a", symptoms: "#c0627d", discharge: "#9c86c4", digestion: "#b5638f", other: "#c8917f", activity: "#6fa585",
};

export default function Track() {
  const [params, setParams] = useSearchParams();
  const tab = params.get("tab") === "day" ? "day" : "period";
  const setTab = (t) => setParams((p) => { p.set("tab", t); return p; }, { replace: true });

  return (
    <Screen>
      <TopBar title="Track" subtitle="Log your period and how you feel" back={false} />
      <div className="seg" style={{ marginBottom: 16 }}>
        <button className={tab === "period" ? "on" : ""} onClick={() => setTab("period")}>Period</button>
        <button className={tab === "day" ? "on" : ""} onClick={() => setTab("day")}>Symptoms &amp; more</button>
      </div>
      {tab === "period" ? <PeriodTab /> : <DayTab initial={params.get("date")} />}
    </Screen>
  );
}

/* ---------------- period ---------------- */
function PeriodTab() {
  const toast = useToast();
  const { data: cycles, error, loading, reload } = useAsync(() => api.cycles());
  const todayIso = toISO(today());
  const [form, setForm] = useState({ start: todayIso, ended: false, end: todayIso, flow: "medium" });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const save = async (e) => {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      await api.addCycle({ start_date: form.start, end_date: form.ended ? form.end : null, flow_level: form.flow });
      toast("Period saved 🌸");
      celebrate();
      reload();
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (c) => {
    if (!window.confirm("Delete the period starting " + fmtDate(c.start_date) + "?")) return;
    try {
      await api.deleteCycle(c.id);
      toast("Deleted");
      reload();
    } catch (ex) {
      toast(ex.message);
    }
  };

  const endNow = async (c) => {
    try {
      await api.updateCycle(c.id, { end_date: todayIso });
      toast("Marked as ended today");
      reload();
    } catch (ex) {
      toast(ex.message);
    }
  };

  return (
    <>
      <form className="card" onSubmit={save}>
        <div className="section-title" style={{ marginTop: 0 }}>Log a period</div>
        <label className="field">
          <span>Start date</span>
          <input className="input" type="date" required max={todayIso} value={form.start}
            onChange={(e) => setForm({ ...form, start: e.target.value })} />
        </label>
        <label className="check">
          <input type="checkbox" checked={form.ended} onChange={(e) => setForm({ ...form, ended: e.target.checked })} />
          My period has ended
        </label>
        {form.ended && (
          <label className="field">
            <span>End date</span>
            <input className="input" type="date" required min={form.start} max={todayIso} value={form.end}
              onChange={(e) => setForm({ ...form, end: e.target.value })} />
          </label>
        )}
        <div className="field">
          <span>Flow</span>
          <div className="chips">
            {["light", "medium", "heavy"].map((f) => (
              <button type="button" key={f} className={"chip" + (form.flow === f ? " on" : "")}
                onClick={() => setForm({ ...form, flow: f })}>
                {"💧".repeat(f === "light" ? 1 : f === "medium" ? 2 : 3)} {f[0].toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
        {err && <div className="alert danger" style={{ marginBottom: 12 }}>{err}</div>}
        <button className="btn block" disabled={busy}>{busy ? "Saving..." : "Save period"}</button>
      </form>

      <div className="section-title">Cycle history</div>
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {cycles && !cycles.length && <div className="card empty muted">No periods logged yet.</div>}
      {cycles && cycles.length > 0 && (
        <div className="card menu">
          {cycles.map((c) => (
            <div className="menu-row" key={c.id}>
              <span className="ic"><Icon name="drop" /></span>
              <div style={{ minWidth: 0 }}>
                <div>{fmtDate(c.start_date)} – {c.end_date ? fmtDate(c.end_date) : "ongoing"}</div>
                <div className="small muted">
                  {c.flow_level} flow
                  {c.end_date && " · " + (Math.round((parseISO(c.end_date) - parseISO(c.start_date)) / 86400000) + 1) + " days"}
                </div>
              </div>
              <span style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
                {!c.end_date && <button className="btn sm outline" onClick={() => endNow(c)}>End today</button>}
                <button className="icon-btn plain" onClick={() => remove(c)} aria-label="Delete"><Icon name="trash" size={19} /></button>
              </span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

/* ---------------- day log ---------------- */
function DayTab({ initial }) {
  const toast = useToast();
  const todayIso = toISO(today());
  const [iso, setIso] = useState(initial && initial <= todayIso ? initial : todayIso);
  const [query, setQuery] = useState("");
  const [tags, setTags] = useState({});
  const [severity, setSeverity] = useState(3);
  const [saving, setSaving] = useState(false);

  const catalog = useAsync(() => api.catalog());
  const cycles = useAsync(() => api.cycles());
  const day = useAsync(() => api.getDay(iso), [iso]);

  useEffect(() => {
    if (day.data) {
      setTags(day.data.tags || {});
      setSeverity(day.data.severity || 3);
    }
  }, [day.data]);

  const cycleDay = useMemo(() => {
    const starts = (cycles.data || []).map((c) => c.start_date).filter((s) => s <= iso).sort();
    if (!starts.length) return null;
    const n = Math.round((parseISO(iso) - parseISO(starts[starts.length - 1])) / 86400000) + 1;
    return n <= 60 ? n : null;
  }, [cycles.data, iso]);

  const toggle = (cat, tag) =>
    setTags((t) => {
      const cur = t[cat] || [];
      return { ...t, [cat]: cur.includes(tag) ? cur.filter((x) => x !== tag) : [...cur, tag] };
    });

  const move = (n) => {
    const next = toISO(addDays(parseISO(iso), n));
    if (next <= todayIso) setIso(next);
  };

  const save = async () => {
    setSaving(true);
    try {
      await api.saveDay(iso, { tags, severity });
      toast("Saved for " + fmtDate(iso, { month: "short", day: "numeric" }) + " ✨");
      celebrate();
    } catch (ex) {
      toast(ex.message);
    } finally {
      setSaving(false);
    }
  };

  const d = parseISO(iso);
  const cats = catalog.data?.categories || [];
  const q = query.trim().toLowerCase();
  const shown = cats.filter((c) => !q || c.title.toLowerCase().includes(q) || c.tags.some((t) => t.toLowerCase().includes(q)));
  const symptomTags = new Set(catalog.data?.symptom_tags || []);
  const hasSymptoms = Object.values(tags).some((list) => list.some((t) => symptomTags.has(t)));

  return (
    <>
      <div className="card date-nav">
        <button className="icon-btn" onClick={() => move(-1)} aria-label="Previous day"><Icon name="left" /></button>
        <div className="d">
          <b>{d.getDate()} {MONTHS[d.getMonth()]} {d.getFullYear()}</b>
          <span className="small muted">
            {cycleDay ? "Cycle day " + cycleDay : d.toLocaleDateString("en-US", { weekday: "long" })}
            {iso === todayIso && " · Today"}
          </span>
        </div>
        <button className="icon-btn" onClick={() => move(1)} disabled={iso >= todayIso} aria-label="Next day"
          style={{ opacity: iso >= todayIso ? 0.4 : 1 }}><Icon name="right" /></button>
      </div>

      <div className="card row" style={{ padding: "4px 16px", marginTop: 12 }}>
        <Icon name="search" size={18} style={{ color: "var(--muted)" }} />
        <input className="input" style={{ border: "none", background: "transparent", boxShadow: "none", paddingLeft: 0 }}
          placeholder="Search symptoms, mood..." value={query} onChange={(e) => setQuery(e.target.value)} />
      </div>

      {(catalog.loading || day.loading) && <Loading />}
      <ErrorBox error={catalog.error || day.error} onRetry={() => { catalog.reload(); day.reload(); }} />

      {!catalog.loading && !day.loading && !catalog.error && (
        <>
          {shown.map((c) => (
            <div className="card" key={c.key} style={{ marginTop: 12 }}>
              <div style={{ fontWeight: 700, color: "var(--plum)", marginBottom: 10 }}>{c.title}</div>
              <div className="chips" style={{ "--chip-on": CAT_COLOR[c.key] || "var(--pink-600)" }}>
                {c.tags.map((t) => (
                  <button key={t} className={"chip" + ((tags[c.key] || []).includes(t) ? " on" : "")} onClick={() => toggle(c.key, t)}>
                    {EMOJI[t] || "•"} {t}
                  </button>
                ))}
              </div>
            </div>
          ))}
          {!shown.length && <div className="card empty muted" style={{ marginTop: 12 }}>Nothing matches your search.</div>}

          {hasSymptoms && (
            <div className="card" style={{ marginTop: 12 }}>
              <div className="row between" style={{ fontWeight: 700, color: "var(--plum)" }}>
                <span>How strong are your symptoms?</span>
                <span>{severity}/5</span>
              </div>
              <input type="range" min="1" max="5" value={severity} onChange={(e) => setSeverity(Number(e.target.value))} />
              <div className="row between small muted"><span>Mild</span><span>Severe</span></div>
            </div>
          )}

          <div style={{ position: "sticky", bottom: "calc(var(--nav-h) + 14px)", marginTop: 16, zIndex: 5 }}>
            <button className="btn block" onClick={save} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
          </div>
        </>
      )}
    </>
  );
}
