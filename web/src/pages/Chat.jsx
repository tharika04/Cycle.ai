import { Fragment, useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../App.jsx";
import { Heart } from "../components/Art.jsx";
import { ART } from "../assets/art/index.js";
import Icon from "../components/Icon.jsx";
import { Screen, Sheet, useAsync, useToast } from "../components/ui.jsx";

const LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam"];
const SUGGESTIONS = {
  menstrual: ["How can I ease my cramps?", "What should I eat during periods?", "Is my flow normal?"],
  follicular: ["What workouts suit this phase?", "Why is my energy rising?", "What should I eat today?"],
  ovulation: ["What is my fertile window?", "What are signs of ovulation?", "What should I eat today?"],
  luteal: ["How can I reduce PMS?", "Why do I crave sugar before my period?", "What should I eat today?"],
};

const newId = () =>
  (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(16) + Math.random().toString(16).slice(2)).replace(/-/g, "");

/* Minimal, safe markdown: **bold**, *italic*, bullet lists, paragraphs. React escapes all text. */
function inline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? <b key={i}>{p.slice(2, -2)}</b>
      : p.startsWith("*") && p.endsWith("*") && p.length > 2 ? <i key={i}>{p.slice(1, -1)}</i>
      : <Fragment key={i}>{p}</Fragment>
  );
}
function Markdown({ text }) {
  const blocks = [];
  let list = null;
  String(text).split("\n").forEach((raw) => {
    const line = raw.trim();
    const m = line.match(/^([-*•]|\d+[.)])\s+(.*)$/);
    if (m) {
      if (!list) blocks.push((list = { type: "ul", items: [] }));
      list.items.push(m[2]);
    } else {
      list = null;
      if (line) blocks.push({ type: "p", text: line.replace(/^#+\s*/, "") });
    }
  });
  return blocks.map((b, i) =>
    b.type === "ul" ? (
      <ul key={i}>{b.items.map((it, j) => <li key={j}>{inline(it)}</li>)}</ul>
    ) : (
      <p key={i}>{inline(b.text)}</p>
    )
  );
}

export default function Chat() {
  const { user } = useAuth();
  const toast = useToast();
  const [convId, setConvId] = useState(newId);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [sheet, setSheet] = useState(false);
  const [language, setLanguage] = useState(() => {
    try { return localStorage.getItem("hr_lang") || "English"; } catch { return "English"; }
  });
  const endRef = useRef(null);
  const pred = useAsync(() => api.predict().catch(() => null));
  const convs = useAsync(() => api.conversations().catch(() => []), [sheet]);

  const phase = pred.data?.status === "ok" ? (pred.data.current_phase === "late" ? "luteal" : pred.data.current_phase) : "menstrual";

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  const pickLanguage = (l) => {
    setLanguage(l);
    try { localStorage.setItem("hr_lang", l); } catch { /* ignore */ }
  };

  const send = async (msg) => {
    const q = (msg ?? text).trim();
    if (!q || busy) return;
    setText("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    try {
      const res = await api.chat(q, language, convId);
      setMessages((m) => [...m, { role: "bot", text: res.response }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, I couldn't answer that: " + e.message, error: true }]);
    } finally {
      setBusy(false);
    }
  };

  const newChat = () => {
    setConvId(newId());
    setMessages([]);
    setSheet(false);
  };

  const openChat = async (id) => {
    try {
      const rows = await api.chatHistory(id);
      setMessages(rows.flatMap((r) => [{ role: "user", text: r.message }, { role: "bot", text: r.response }]));
      setConvId(id);
      setSheet(false);
    } catch (e) {
      toast(e.message);
    }
  };

  const deleteChat = async () => {
    try {
      await api.deleteChat(convId);
      toast("Chat deleted");
    } catch (e) {
      toast(e.message);
    }
    newChat();
  };

  const first = (user?.name || "").split(" ")[0];

  return (
    <Screen className="chat-screen">
      <div className="row between">
        <span />
        <button className="icon-btn" onClick={() => setSheet(true)} aria-label="Chats and language"><Icon name="menu" /></button>
      </div>

      <div className="chat-hero">
        <div className="bot-ring bob"><div><img src={ART.herbot} alt="HerBot" /></div></div>
        <h1>HerBot</h1>
        <div className="subtitle" style={{ display: "flex", alignItems: "center", gap: 5 }}>
          Your AI health companion <Heart size={14} />
        </div>
      </div>

      <div className="msg bot">
        <span className="bot-mini"><img src={ART.herbot} alt="" /></span>
        <div className="bubble">
          <p>Hi{first ? " " + first : ""}! 👋</p>
          <p>How can I help you today?</p>
        </div>
      </div>

      {messages.length === 0 && (
        <div className="suggest">
          {SUGGESTIONS[phase].map((s) => (
            <button key={s} onClick={() => send(s)}>{s}</button>
          ))}
        </div>
      )}

      {messages.map((m, i) => (
        <div key={i} className={"msg " + (m.role === "user" ? "user" : "bot")}>
          {m.role === "bot" && <span className="bot-mini"><img src={ART.herbot} alt="" /></span>}
          <div className="bubble" style={m.error ? { color: "#8a1f1f" } : undefined}>
            {m.role === "bot" ? <Markdown text={m.text} /> : m.text}
          </div>
        </div>
      ))}
      {busy && (
        <div className="msg bot">
          <span className="bot-mini"><img src={ART.herbot} alt="" /></span>
          <div className="bubble"><span className="typing"><i /><i /><i /></span></div>
        </div>
      )}
      <p className="center small muted" style={{ marginTop: 10 }}>General information only, not medical advice.</p>
      <div ref={endRef} />

      <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type your question..." maxLength={1000} aria-label="Your question" />
        <button disabled={busy || !text.trim()} aria-label="Send"><Icon name="send" size={19} /></button>
      </form>

      <Sheet open={sheet} onClose={() => setSheet(false)}>
        <div className="field">
          <span>Reply language</span>
          <div className="chips">
            {LANGUAGES.map((l) => (
              <button key={l} className={"chip" + (l === language ? " on" : "")} onClick={() => pickLanguage(l)}>{l}</button>
            ))}
          </div>
        </div>
        <div className="row" style={{ marginBottom: 16 }}>
          <button className="btn sm" onClick={newChat}><Icon name="plus" size={16} /> New chat</button>
          {messages.length > 0 && <button className="btn sm outline" onClick={deleteChat}><Icon name="trash" size={16} /> Delete this chat</button>}
        </div>
        <div className="field"><span>Past chats</span></div>
        {(convs.data || []).length === 0 && <p className="small muted">No past chats yet.</p>}
        <div className="card menu" style={{ display: (convs.data || []).length ? "block" : "none" }}>
          {(convs.data || []).slice(0, 15).map((c) => (
            <button key={c.id} className="menu-row" onClick={() => openChat(c.id)}>
              <span className="ic"><Icon name="chat" size={18} /></span>
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {c.id === "legacy" ? "Earlier chats: " : ""}{c.title || "Chat"}
              </span>
              {c.id === convId && <span className="small" style={{ marginLeft: "auto", color: "var(--pink-600)" }}>open</span>}
            </button>
          ))}
        </div>
      </Sheet>
    </Screen>
  );
}
