import { useState } from "react";
import { api, downloadBlob } from "../api.js";
import { useAuth } from "../App.jsx";
import Icon from "../components/Icon.jsx";
import { Screen, TopBar, useToast } from "../components/ui.jsx";

export default function Settings() {
  const toast = useToast();
  const { logout } = useAuth();
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);

  const exportData = async () => {
    try {
      const data = await api.exportData();
      downloadBlob(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }), "herrhythm_my_data.json");
      toast("Your data was downloaded");
    } catch (e) {
      toast(e.message);
    }
  };

  const remove = async () => {
    setBusy(true);
    try {
      await api.deleteAccount();
      toast("Your account and all data were deleted.");
      logout();
    } catch (e) {
      toast(e.message);
      setBusy(false);
    }
  };

  return (
    <Screen>
      <TopBar title="Privacy & Security" subtitle="Your data, your control" />
      <div className="card">
        <div style={{ fontWeight: 700, color: "var(--plum)" }}>Export my data</div>
        <p className="small muted" style={{ margin: "4px 0 12px" }}>Download everything HerRhythm has stored about you as a JSON file.</p>
        <button className="btn block ghost" onClick={exportData}><Icon name="download" size={18} /> Download my data</button>
      </div>

      <div className="card">
        <div style={{ fontWeight: 700, color: "var(--plum)" }}>Delete my account</div>
        <div className="alert danger" style={{ margin: "10px 0 12px" }}>
          This permanently deletes your account, periods, symptoms and chat history. It cannot be undone.
        </div>
        <label className="check">
          <input type="checkbox" checked={confirm} onChange={(e) => setConfirm(e.target.checked)} />
          I understand and want to delete everything
        </label>
        <button className="btn block danger" disabled={!confirm || busy} onClick={remove}>
          <Icon name="trash" size={18} /> {busy ? "Deleting..." : "Delete my account"}
        </button>
      </div>

      <div className="card">
        <div style={{ fontWeight: 700, color: "var(--plum)" }}>How your data is kept</div>
        <ul className="small muted" style={{ margin: "6px 0 0", paddingLeft: 18, lineHeight: 1.6 }}>
          <li>Your password is stored only as a secure hash.</li>
          <li>Your logs are linked to your account and never shared.</li>
          <li>You are signed out automatically after 24 hours.</li>
        </ul>
      </div>
    </Screen>
  );
}
