// Thin client for the HerRhythm FastAPI backend.
// In dev the backend runs on :8000; in production the backend serves this app, so paths are same-origin.
export const API_URL =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

const TOKEN_KEY = "hr_token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable */
  }
}

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

async function request(method, path, { body, form, params, raw } = {}) {
  let url = API_URL + path;
  if (params) {
    const q = new URLSearchParams(params).toString();
    if (q) url += "?" + q;
  }
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = "Bearer " + token;
  let payload;
  if (form) {
    payload = new URLSearchParams(form);
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(url, { method, headers, body: payload });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }
  if (res.status === 401 && token) {
    setToken(null);
    onUnauthorized();
    throw new Error("Your session expired. Please log in again.");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : data.detail?.[0]?.msg || detail;
    } catch {
      /* not JSON */
    }
    throw new Error(detail || "Something went wrong");
  }
  return raw ? res : res.json();
}

export const api = {
  // auth
  login: (email, password) =>
    request("POST", "/auth/login", { form: { username: email, password } }).then((r) => r.access_token),
  register: (data) => request("POST", "/auth/register", { body: data }),
  me: () => request("GET", "/account/me"),

  // cycles & prediction
  cycles: () => request("GET", "/cycles"),
  addCycle: (data) => request("POST", "/cycles", { body: data }),
  updateCycle: (id, data) => request("PUT", "/cycles/" + id, { body: data }),
  deleteCycle: (id) => request("DELETE", "/cycles/" + id),
  predict: () => request("GET", "/predict"),

  // symptoms & day log
  symptoms: () => request("GET", "/symptoms"),
  addSymptom: (data) => request("POST", "/symptoms", { body: data }),
  catalog: () => request("GET", "/daylog/catalog"),
  loggedDates: () => request("GET", "/daylog/dates"),
  getDay: (iso) => request("GET", "/daylog/" + iso),
  saveDay: (iso, data) => request("PUT", "/daylog/" + iso, { body: data }),

  // wellness
  plan: (phase, diet) => request("GET", "/plan", { params: { phase, diet } }),
  screening: () => request("GET", "/wellness/screening"),
  reminders: () => request("GET", "/wellness/reminders"),
  emailReminders: () => request("POST", "/wellness/reminders/email", { body: {} }),
  insights: () => request("GET", "/account/insights"),
  routines: () => request("GET", "/routines"),
  figureUrl: (name) => API_URL + "/routines/figure/" + name,

  // chat
  chat: (message, language, conversation_id) =>
    request("POST", "/chat", { body: { message, language, conversation_id } }),
  conversations: () => request("GET", "/chat/conversations"),
  chatHistory: (conversation_id) => request("GET", "/chat/history", { params: { conversation_id } }),
  deleteChat: (conversation_id) => request("DELETE", "/chat/history", { params: { conversation_id } }),

  // account
  exportData: () => request("GET", "/account/export"),
  deleteAccount: () => request("DELETE", "/account"),
  reportBlob: () => request("GET", "/account/report", { raw: true }).then((r) => r.blob()),
};

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
