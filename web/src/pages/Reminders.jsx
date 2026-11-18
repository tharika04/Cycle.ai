import { useState } from "react";
import { api } from "../api.js";
import Icon from "../components/Icon.jsx";
import { ErrorBox, Loading, Screen, TopBar, useAsync, useToast } from "../components/ui.jsx";

const KIND = { late: ["watch", "⏰"], period: ["info", "🩸"], fertile: ["ok", "🌿"], log: ["info", "📝"], tip: ["ok", "💡"] };

export default function Reminders() {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const { data, error, loading, reload } = useAsync(() => api.reminders());

  const email = async () => {
    setBusy(true);
    try {
      const res = await api.emailReminders();
      toast("Sent to " + res.to + ". Check your inbox and spam.");
    } catch (e) {
      toast(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Screen>
      <TopBar title="Notifications" subtitle="Your reminders for today" />
      {loading && <Loading />}
      <ErrorBox error={error} onRetry={reload} />
      {data && (
        <>
          {data.reminders.map((r, i) => {
            const [cls, emoji] = KIND[r.kind] || KIND.log;
            return (
              <div key={i} className={"alert " + cls}>
                <b>{emoji} {r.title}</b>
                {r.message}
              </div>
            );
          })}
          <div className="card" style={{ marginTop: 18 }}>
            <div style={{ fontWeight: 700, color: "var(--plum)" }}>Email me my reminders</div>
            <p className="small muted" style={{ margin: "4px 0 12px" }}>Sends today's reminders to {data.email_hint}.</p>
            <button className="btn block" onClick={email} disabled={busy}>
              <Icon name="mail" size={18} /> {busy ? "Sending..." : "Send to my email"}
            </button>
          </div>
          <p className="small muted center" style={{ marginTop: 12 }}>Reminders are estimates based on your logs, not medical advice.</p>
        </>
      )}
    </Screen>
  );
}
