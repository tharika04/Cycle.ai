// Small line-icon set (24x24, stroke based) so the app has no icon-font dependency.
const PATHS = {
  home: "M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
  calendar: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4",
  chat: "M4 5h16v11H9l-5 4z M8 10h.01 M12 10h.01 M16 10h.01",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
  plus: "M12 5v14M5 12h14",
  bell: "M6 16V11a6 6 0 1 1 12 0v5l2 2H4zM10 20a2 2 0 0 0 4 0",
  back: "M15 5l-7 7 7 7",
  chevron: "M9 6l6 6-6 6",
  left: "M14 6l-6 6 6 6",
  right: "M10 6l6 6-6 6",
  send: "M4 12 20 4l-6 16-3-7z",
  gear: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z",
  history: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4M8 14h3M8 17h6",
  report: "M6 3h9l4 4v14H6zM14 3v5h5M9 13l2 2 4-4",
  lock: "M6 11h12v10H6zM8 11V8a4 4 0 0 1 8 0v3",
  info: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v6M12 7.5h.01",
  help: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01",
  logout: "M10 4H5v16h5M14 8l4 4-4 4M18 12H9",
  drop: "M12 3C9 8 6 11 6 15a6 6 0 0 0 12 0c0-4-3-7-6-12z",
  spark: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z",
  heart: "M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z",
  bulb: "M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z",
  search: "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4",
  trash: "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
  close: "M6 6l12 12M18 6 6 18",
  menu: "M4 7h16M4 12h16M4 17h16",
  download: "M12 4v11M7 10l5 5 5-5M5 20h14",
  mail: "M4 6h16v12H4zM4 7l8 6 8-6",
  body: "M12 7a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM7 9h10l-1.5 6h-2l-.5 7h-2l-.5-7h-2z",
  play: "M8 5v14l11-7z",
  pause: "M8 5v14M16 5v14",
  timer: "M12 21a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM12 9v4l2 2M10 2h4",
  edit: "M4 20h4L19 9l-4-4L4 16zM14 6l4 4",
  leaf: "M5 19C5 10 11 5 20 4c0 9-5 15-14 15zM5 19l8-8",
  arrow: "M5 12h14M13 6l6 6-6 6",
};

export default function Icon({ name, size = 22, stroke = 2, fill = "none", className, style }) {
  const d = PATHS[name];
  if (!d) return null;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={fill}
      stroke="currentColor"
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={style}
      aria-hidden="true"
    >
      <path d={d} />
    </svg>
  );
}
