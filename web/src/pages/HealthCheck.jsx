import { Link } from "react-router-dom";
import { api } from "../api.js";
import { ErrorBox, Loading, Screen, TopBar, useAsync } from "../components/ui.jsx";

const LEVEL = { see_doctor: "danger", watch: "watch", ok: "ok", info: "info" };
const OVERALL = {
  see_doctor: ["danger", "Something in your logs is worth discussing with a doctor soon."],
  watch: ["watch", "A few things are worth keeping an eye on."],
  ok: ["ok", "No flags from your logged data. 🌸"],
};

export default function HealthCheck() {
  const { data, error, loading, reload } = useAsync(() => api.screening());
  return (
    <Screen>
      <TopBar title="Health Check" subtitle="A simple screening of your logged data" />
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
          <div className={"alert " + OVERALL[data.overall][0]} style={{ fontSize: "0.95rem" }}>
            <b>{OVERALL[data.overall][1]}</b>
            Cycles analysed: {data.cycles_analyzed}
          </div>
          <div className="section-title">Findings</div>
          {data.findings.map((f, i) => (
            <div key={i} className={"alert " + LEVEL[f.level]}>
              <b>{f.title}</b>
              {f.detail}
            </div>
          ))}
          <p className="small muted" style={{ marginTop: 16, lineHeight: 1.5 }}>{data.disclaimer}</p>
        </>
      )}
    </Screen>
  );
}
