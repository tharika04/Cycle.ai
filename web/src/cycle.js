// Date helpers and calendar colouring, ported from the old Streamlit cycle_marks.py.

export const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
export const WEEKDAYS = ["M", "T", "W", "T", "F", "S", "S"];

export const PHASE_TIPS = {
  menstrual: "Rest, stay warm and hydrated, and eat iron-rich foods. Gentle walking helps.",
  follicular: "Energy is rising. A good time for strength training and new projects.",
  ovulation: "Many people feel most energetic and social around now.",
  luteal: "PMS may show up. Magnesium-rich foods and light exercise can help.",
  late: "Your period is later than predicted. Log it when it starts.",
};

export const MARK_STYLE = {
  pl: { bg: "#c0627d", fg: "#ffffff", label: "Period" },
  pp: { bg: "#f3cdd6", fg: "#8f3a54", label: "Predicted" },
  fw: { bg: "#cfe5d5", fg: "#2e5a3e", label: "Fertile" },
  ov: { bg: "#e9c88f", fg: "#5a3f12", label: "Ovulation" },
};

// ISO "YYYY-MM-DD" <-> local Date (no timezone shifting)
export function parseISO(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}
export function toISO(d) {
  const p = (n) => String(n).padStart(2, "0");
  return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate());
}
export function addDays(d, n) {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  x.setDate(x.getDate() + n);
  return x;
}
export function today() {
  const n = new Date();
  return new Date(n.getFullYear(), n.getMonth(), n.getDate());
}
export function daysInMonth(y, m) {
  return new Date(y, m + 1, 0).getDate();
}
export function fmtDate(iso, opts = { month: "short", day: "numeric", year: "numeric" }) {
  return parseISO(iso).toLocaleDateString("en-US", opts);
}

/** Weeks of a month (Monday first). Each week is 7 entries of day number or 0. */
export function monthWeeks(y, m) {
  const first = (new Date(y, m, 1).getDay() + 6) % 7;
  const n = daysInMonth(y, m);
  const cells = Array(first).fill(0);
  for (let d = 1; d <= n; d++) cells.push(d);
  while (cells.length % 7) cells.push(0);
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  return weeks;
}

/** Sets of ISO dates: logged period, predicted period, fertile window, ovulation. */
export function buildMarks(cycles, pred, now = today()) {
  const marks = { logged: new Set(), predicted: new Set(), fertile: new Set(), ovulation: new Set() };
  if (!pred || pred.status !== "ok" || !cycles?.length) return marks;
  const P = Number(pred.avg_period_length);
  const L = Number(pred.avg_cycle_length);
  const ordered = [...cycles].sort((a, b) => a.start_date.localeCompare(b.start_date));
  const nextOriginal = parseISO(pred.next_period_start);

  const addFertile = (ov) => {
    marks.ovulation.add(toISO(ov));
    for (let k = -5; k <= 1; k++) marks.fertile.add(toISO(addDays(ov, k)));
  };

  ordered.forEach((c, i) => {
    const start = parseISO(c.start_date);
    let end = c.end_date ? parseISO(c.end_date) : addDays(start, P - 1);
    if (!c.end_date && end > now) end = now;
    if (end < start) end = start;
    for (let d = start; d <= end; d = addDays(d, 1)) marks.logged.add(toISO(d));

    let nxt;
    if (i + 1 < ordered.length) {
      nxt = parseISO(ordered[i + 1].start_date);
      const gap = Math.round((nxt - start) / 86400000);
      if (gap < 15 || gap > 60) nxt = addDays(start, L);
    } else {
      nxt = nextOriginal;
    }
    addFertile(addDays(nxt, -14));
  });

  const base = nextOriginal > now ? nextOriginal : now;
  const horizon = new Date(now.getFullYear() + 1, 11, 31);
  for (let k = 0; ; k++) {
    const start = addDays(base, k * L);
    if (start > horizon) break;
    for (let j = 0; j < P; j++) marks.predicted.add(toISO(addDays(start, j)));
    if (k >= 1) addFertile(addDays(start, -14));
  }
  return marks;
}

export function dayClass(iso, marks) {
  if (marks.logged.has(iso)) return "pl";
  if (marks.predicted.has(iso)) return "pp";
  if (marks.ovulation.has(iso)) return "ov";
  if (marks.fertile.has(iso)) return "fw";
  return "";
}

export function periodLine(pred) {
  const left = Number(pred.days_until_next_period);
  if (left > 0) return "Period in " + left + " day" + (left === 1 ? "" : "s");
  if (left === 0) return "Period expected today";
  return -left + " day" + (left === -1 ? "" : "s") + " late";
}

export function titleCase(s) {
  return String(s || "").replace(/\b\w/g, (c) => c.toUpperCase());
}
