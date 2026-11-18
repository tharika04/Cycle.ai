import { useState } from "react";
import { Link } from "react-router-dom";
import { api, downloadBlob } from "../api.js";
import Icon from "../components/Icon.jsx";
import { Bars, ErrorBox, Loading, Screen, TopBar, useAsync, useToast } from "../components/ui.jsx";
import { titleCase } from "../cycle.js";

const PHASES = [
  ["menstrual", "#c0627d"],
  ["follicular", "#b6a1cf"],
  ["ovulation", "#e2bd7f"],
  ["luteal", "#8fbfa6"],
];
const sevColor = (s) => `hsl(345, 42%, ${84 - s * 8}%)`;

export default function Insights() {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const { data, error, loading, reload } = useAsync(() => api.insights());

  const download = async () => {
    setBusy(true);
    try {
      downloadBlob(await api.reportBlob(), "herrhythm_report.pdf");
      toast("Report downloaded");
    } catch (e) {
      toast(e.message);
    } finally {
      setBusy(false);
    }
  };

  const pred = data?.prediction;
  const rows = data?.symptoms || [];

  return (
    <Screen>
      <TopBar title="Health Reports" subtitle="Your patterns and a doctor-ready summary" />
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && data.status !== "ok" && (
        <div className="card empty">
          <p>{data.message}</p>
          <Link className="btn" to="/track?tab=period">Log a period</Link>
        </div>
      )}
      {data?.status === "ok" && (
        <>
          <div className="grid-2">
            <div className="card stat"><div className="v">{pred.cycles_logged}</div><div className="l">Cycles logged</div></div>
            <div className="card stat"><div className="v">{pred.avg_cycle_length} days</div><div className="l">Average cycle</div></div>
            <div className="card stat"><div className="v">{pred.avg_period_length} days</div><div className="l">Average period</div></div>
            <div className="card stat"><div className="v">{pred.irregular ? "Irregular" : "Regular"}</div><div className="l">Regularity</div></div>
          </div>

          <div className="section-title">Symptoms by cycle phase</div>
          {rows.length === 0 ? (
            <div className="card empty muted">
              Log some symptoms to see patterns. <Link className="link" to="/track?tab=day">Log today</Link>
            </div>
          ) : (
            <div className="card">
              <div className="legend" style={{ marginTop: 0, marginBottom: 12 }}>
                {PHASES.map(([p, c]) => <span key={p}><i style={{ background: c }} />{titleCase(p)}</span>)}
              </div>
              <Bars
                rows={rows.slice(0, 10).map((r) => ({
                  label: titleCase(r.symptom.replace("pain - ", "pain: ")),
                  value: r.count,
                  parts: PHASES.filter(([p]) => r.by_phase[p]).map(([p, c]) => ({
                    value: r.by_phase[p], color: c, title: titleCase(p) + ": " + r.by_phase[p],
                  })),
                }))}
              />
            </div>
          )}

          {rows.length > 0 && (
            <>
              <div className="section-title">Average severity</div>
              <div className="card">
                <Bars
                  max={5}
                  rows={rows.slice(0, 10).map((r) => ({
                    label: titleCase(r.symptom.replace("pain - ", "pain: ")),
                    value: r.avg_severity,
                    display: r.avg_severity,
                  }))}
                  colorFor={(r) => sevColor(r.value)}
                />
              </div>
              <div className="section-title">What we noticed</div>
              {rows.slice(0, 6).map((r) => (
                <div className="card small" key={r.symptom} style={{ lineHeight: 1.5 }}>
                  <b style={{ color: "var(--plum)" }}>{titleCase(r.symptom)}</b>: logged {r.count} time(s), average severity{" "}
                  {r.avg_severity}/5, most often in the {r.top_phase} phase ({r.top_phase_share}% of entries).
                </div>
              ))}
              <p className="small muted center" style={{ marginTop: 10 }}>More logged days give more reliable patterns.</p>
            </>
          )}

          <div className="card" style={{ marginTop: 18 }}>
            <div style={{ fontWeight: 700, color: "var(--plum)" }}>Doctor-ready report</div>
            <p className="small muted" style={{ margin: "4px 0 12px" }}>A one-page PDF summary you can share with your doctor.</p>
            <button className="btn block" onClick={download} disabled={busy}>
              <Icon name="download" size={18} /> {busy ? "Preparing..." : "Download PDF report"}
            </button>
          </div>
        </>
      )}
    </Screen>
  );
}
