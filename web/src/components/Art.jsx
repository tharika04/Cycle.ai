// Hand-drawn SVG illustrations matching the client's pink mockups.

export function Lotus({ size = 120 }) {
  const petals = [
    { a: -68, c: "#f6b3cb" },
    { a: 68, c: "#f6b3cb" },
    { a: -40, c: "#ee86ab" },
    { a: 40, c: "#ee86ab" },
    { a: -16, c: "#e0508a" },
    { a: 16, c: "#e0508a" },
  ];
  return (
    <svg width={size} height={size * 0.8} viewBox="0 0 120 96" aria-label="HerRhythm lotus logo">
      <defs>
        <linearGradient id="lotusDrop" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f0679a" />
          <stop offset="1" stopColor="#b8235f" />
        </linearGradient>
      </defs>
      {petals.map((p, i) => (
        <path
          key={i}
          d="M60 80 C44 60 46 32 60 16 C74 32 76 60 60 80Z"
          fill={p.c}
          opacity="0.95"
          transform={`rotate(${p.a} 60 80)`}
        />
      ))}
      <path d="M60 80 C40 84 22 80 10 70 C28 66 46 70 60 80Z" fill="#f2a0bf" />
      <path d="M60 80 C80 84 98 80 110 70 C92 66 74 70 60 80Z" fill="#f2a0bf" />
      <path d="M60 10 C52 24 44 34 44 46 a16 16 0 0 0 32 0 C76 34 68 24 60 10Z" fill="url(#lotusDrop)" />
      <ellipse cx="54" cy="44" rx="3.5" ry="6" fill="#fff" opacity="0.45" />
    </svg>
  );
}

export function Leaves({ width = 90, flip = false, opacity = 0.9, style }) {
  return (
    <svg
      width={width}
      viewBox="0 0 100 140"
      style={{ transform: flip ? "scaleX(-1)" : undefined, opacity, ...style }}
      aria-hidden="true"
    >
      <path d="M20 138 C34 100 52 64 86 20" stroke="#e98bb0" strokeWidth="2.4" fill="none" strokeLinecap="round" />
      {[
        [32, 110, -40], [44, 86, -30], [56, 64, -24], [70, 42, -18],
        [26, 100, 60], [40, 76, 64], [54, 54, 70],
      ].map(([x, y, r], i) => (
        <path
          key={i}
          d="M0 0 C6 -10 18 -12 26 -6 C18 2 6 4 0 0Z"
          fill={i % 2 ? "#f3a9c4" : "#ec8fb3"}
          transform={`translate(${x} ${y}) rotate(${r})`}
        />
      ))}
    </svg>
  );
}

export function Heart({ size = 22, color = "#f07fa6", style }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={style} aria-hidden="true">
      <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" fill={color} />
    </svg>
  );
}

/** Side profile of a woman with closed eyes and long flowing hair (splash screen). */
export function WomanProfile({ style, className }) {
  return (
    <svg viewBox="0 0 360 430" style={style} className={className} preserveAspectRatio="xMinYMax meet" aria-hidden="true">
      <defs>
        <linearGradient id="wpHair" x1="0.2" y1="0" x2="0.5" y2="1">
          <stop offset="0" stopColor="#e889ae" />
          <stop offset="0.55" stopColor="#d6588c" />
          <stop offset="1" stopColor="#c03f74" />
        </linearGradient>
        <linearGradient id="wpSkin" x1="0.2" y1="0" x2="0.9" y2="1">
          <stop offset="0" stopColor="#fde1ea" />
          <stop offset="0.6" stopColor="#f8c4d5" />
          <stop offset="1" stopColor="#f0a6c0" />
        </linearGradient>
        <linearGradient id="wpFade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0.7" stopColor="#fff" stopOpacity="1" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <mask id="wpMask">
          <rect width="360" height="430" fill="url(#wpFade)" />
        </mask>
      </defs>
      <g mask="url(#wpMask)">
        {/* face, neck and shoulders */}
        <path
          fill="url(#wpSkin)"
          d="M232 96 C246 104 252 120 250 136 C250 142 252 146 256 152 C262 160 268 166 273 173
             C275 177 271 181 264 181 C263 184 263 186 264 188 C268 190 267 193 262 195
             C266 198 265 203 259 205 C258 210 262 214 261 219 C260 228 252 232 244 232
             C238 233 234 238 234 246 C234 270 238 292 252 310 C280 330 300 370 306 430 L100 430
             C116 380 150 345 175 320 C188 300 190 270 188 240 C186 200 196 130 232 96 Z"
        />
        {/* soft shadow under the jaw */}
        <path d="M244 232 C238 233 234 238 234 246 C232 240 226 236 218 236 C226 234 236 233 244 232Z" fill="#e48aab" opacity="0.5" />
        {/* hair, back volume flowing down to the left */}
        <path
          fill="url(#wpHair)"
          d="M234 94 C238 78 224 60 200 56 C170 52 144 64 130 88 C118 108 116 130 120 152
             C124 176 112 196 106 214 C100 232 104 252 96 270 C88 292 74 304 74 330
             C74 356 56 380 36 404 C28 414 22 422 18 430 L150 430 C152 404 164 384 168 360
             C172 336 186 318 192 296 C198 272 196 248 202 226 C206 208 204 190 208 172
             C212 150 212 128 226 112 C230 106 236 102 234 94 Z"
        />
        {/* glossy highlight on the crown */}
        <path d="M146 92 C164 72 190 64 214 70" stroke="#fff" strokeWidth="5" strokeLinecap="round" fill="none" opacity="0.3" />
        <path d="M136 118 C140 104 146 96 154 90" stroke="#fff" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.25" />
        {/* fringe sweeping over the forehead */}
        <path fill="url(#wpHair)" d="M234 92 C248 96 254 110 252 124 C246 110 236 104 222 106 C226 100 230 96 234 92Z" />
        {/* hair strands */}
        <g fill="none" stroke="#f8c6d8" strokeLinecap="round" opacity="0.75">
          <path strokeWidth="2" d="M196 64 C160 70 140 98 142 136 C144 170 130 196 122 226 C116 252 106 280 96 310 C88 336 72 366 52 400" />
          <path strokeWidth="1.6" d="M214 74 C186 86 170 114 170 150 C170 186 158 214 150 246 C144 274 136 300 128 330 C120 360 112 390 104 426" />
          <path strokeWidth="1.4" d="M224 92 C206 104 196 128 196 160 C196 192 186 214 182 244" />
          <path strokeWidth="1.2" d="M168 66 C144 82 132 112 134 148 C136 182 116 212 108 246" opacity="0.6" />
        </g>
        <g fill="none" stroke="#b33467" strokeLinecap="round" opacity="0.3">
          <path strokeWidth="1.6" d="M186 70 C158 84 152 116 156 152 C160 188 142 222 134 256 C126 290 108 330 88 380 C80 400 72 414 66 428" />
          <path strokeWidth="1.2" d="M204 196 C198 236 188 266 180 300" />
        </g>
        {/* eyebrow, closed eye and lashes */}
        <path d="M229 137 C236 132 244 132 251 136" stroke="#a53766" strokeWidth="2" fill="none" strokeLinecap="round" />
        <path d="M231 151 C236 157 243 157 248 151" stroke="#8f2556" strokeWidth="2.4" fill="none" strokeLinecap="round" />
        <path d="M233 154 l-3 5 M237 156 l-2 5.5 M241.5 156.5 l-0.5 5.5 M245.5 154.5 l1 5" stroke="#8f2556" strokeWidth="1.4" strokeLinecap="round" />
        {/* nostril, blush, lips */}
        <path d="M262 177 C264 178 266 178 267 177" stroke="#d67699" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        <ellipse cx="240" cy="180" rx="11" ry="7" fill="#f28fb2" opacity="0.35" />
        <path d="M263 188 C268 190 267 193 262 195 C266 198 265 202 259 204 C259 199 260 194 263 188Z" fill="#d85b8b" />
        <path d="M262 195 L257 195" stroke="#b33467" strokeWidth="1.2" strokeLinecap="round" />
        {/* small earring peeking out from the hair */}
        <circle cx="208" cy="214" r="3" fill="#fff" opacity="0.9" />
      </g>
    </svg>
  );
}

/* ---------- flowers, leaves and petals used as decoration on every screen ---------- */

/** One five-petal blossom. */
export function Blossom({ size = 40, color = "#f48fb1", center = "#fff1b8", style, className }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" style={style} className={className} aria-hidden="true">
      {[0, 72, 144, 216, 288].map((a) => (
        <ellipse key={a} cx="20" cy="10.5" rx="7.2" ry="9.5" fill={color} transform={`rotate(${a} 20 20)`} />
      ))}
      {[36, 108, 180, 252, 324].map((a) => (
        <ellipse key={a} cx="20" cy="13" rx="3" ry="5.5" fill="#fff" opacity="0.28" transform={`rotate(${a} 20 20)`} />
      ))}
      <circle cx="20" cy="20" r="5" fill={center} />
      <circle cx="20" cy="20" r="2.2" fill="#f2a33a" opacity="0.7" />
    </svg>
  );
}

/** A curved stem with leaves and pink blossoms, swaying gently. */
export function FlowerSpray({ width = 120, flip = false, style, className = "" }) {
  return (
    <div className={"spray " + className} style={{ width, transform: flip ? "scaleX(-1)" : undefined, ...style }} aria-hidden="true">
      <svg viewBox="0 0 120 160" className="sway">
        <path d="M18 158 C30 120 50 80 98 26" stroke="#e98bb0" strokeWidth="2.4" fill="none" strokeLinecap="round" />
        <path d="M46 96 C60 88 74 86 88 92" stroke="#e98bb0" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {[
          [28, 128, -40], [38, 108, -32], [52, 84, -26], [68, 62, -18],
          [24, 118, 60], [36, 96, 64], [50, 72, 70], [74, 92, 10],
        ].map(([x, y, r], i) => (
          <path key={i} d="M0 0 C6 -10 20 -12 28 -6 C20 3 6 4 0 0Z" fill={i % 2 ? "#f3a9c4" : "#e88db1"} transform={`translate(${x} ${y}) rotate(${r})`} />
        ))}
        <g transform="translate(84 10)"><Petal5 r={14} color="#f06f9e" /></g>
        <g transform="translate(80 80)"><Petal5 r={10} color="#f7a8c4" /></g>
        <g transform="translate(58 40)"><Petal5 r={8} color="#fbc3d6" /></g>
      </svg>
    </div>
  );
}

function Petal5({ r, color }) {
  return (
    <g>
      {[0, 72, 144, 216, 288].map((a) => (
        <ellipse key={a} cx={r} cy={r * 0.5} rx={r * 0.36} ry={r * 0.5} fill={color} transform={`rotate(${a} ${r} ${r})`} />
      ))}
      <circle cx={r} cy={r} r={r * 0.25} fill="#fff1b8" />
    </g>
  );
}

/** Petals drifting down slowly in the background. */
export function FallingPetals({ count = 6 }) {
  const petals = Array.from({ length: count }, (_, i) => ({
    left: (i * 97) % 100,
    delay: (i * 2.3) % 11,
    dur: 11 + ((i * 3) % 7),
    size: 9 + ((i * 5) % 8),
    color: ["#f2c7bd", "#dc96a6", "#f5d9df", "#e6c2b3"][i % 4],
  }));
  return (
    <div className="petals" aria-hidden="true">
      {petals.map((p, i) => (
        <svg
          key={i}
          viewBox="0 0 20 20"
          width={p.size}
          height={p.size}
          style={{ left: p.left + "%", animationDelay: p.delay + "s", animationDuration: p.dur + "s" }}
        >
          <path d="M10 1 C16 5 18 12 10 19 C2 12 4 5 10 1Z" fill={p.color} />
        </svg>
      ))}
    </div>
  );
}

export function CalendarArt({ style }) {
  return (
    <svg viewBox="0 0 300 220" style={style} aria-hidden="true">
      <ellipse cx="150" cy="190" rx="120" ry="20" fill="#f7cbdb" opacity="0.6" />
      {/* side branches */}
      <g opacity="0.95">
        <path d="M40 196 C50 160 62 136 84 112" stroke="#e98bb0" strokeWidth="2" fill="none" />
        {[[50, 172, -50], [58, 150, -40], [70, 128, -30], [46, 164, 50], [56, 140, 60]].map(([x, y, r], i) => (
          <path key={i} d="M0 0 C6 -10 18 -12 26 -6 C18 2 6 4 0 0Z" fill="#ef9bbb" transform={`translate(${x} ${y}) rotate(${r})`} />
        ))}
        <path d="M262 196 C252 160 240 136 218 112" stroke="#e98bb0" strokeWidth="2" fill="none" />
        {[[252, 172, -130], [244, 150, -140], [232, 128, -150], [256, 164, 130], [246, 140, 120]].map(([x, y, r], i) => (
          <path key={i} d="M0 0 C6 -10 18 -12 26 -6 C18 2 6 4 0 0Z" fill="#ef9bbb" transform={`translate(${x} ${y}) rotate(${r})`} />
        ))}
      </g>
      {/* calendar */}
      <rect x="82" y="40" width="140" height="140" rx="18" fill="#fff" stroke="#f3b6cc" strokeWidth="2" />
      <path d="M82 58 a18 18 0 0 1 18 -18 h104 a18 18 0 0 1 18 18 v20 H82z" fill="#ec6f9e" />
      {[110, 194].map((x) => (
        <rect key={x} x={x - 5} y="28" width="10" height="26" rx="5" fill="#c7477c" />
      ))}
      {Array.from({ length: 4 }).map((_, r) =>
        Array.from({ length: 5 }).map((_, c) =>
          r === 1 && (c === 2 || c === 1 || c === 3) ? null : (
            <rect key={r + "-" + c} x={98 + c * 22} y={92 + r * 20} width="12" height="9" rx="2.5" fill="#fbd6e3" />
          )
        )
      )}
      <path d="M152 96 C146 106 140 112 140 120 a12 12 0 0 0 24 0 C164 112 158 106 152 96Z" fill="#d63a72" />
      <ellipse cx="148" cy="118" rx="2.5" ry="4" fill="#fff" opacity="0.5" />
      <g transform="translate(236 34)">
        <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" fill="#f07fa6" />
      </g>
    </svg>
  );
}

export function Robot({ size = 96 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-label="HerBot">
      <defs>
        <linearGradient id="rbHead" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="1" stopColor="#efe4f2" />
        </linearGradient>
      </defs>
      <line x1="50" y1="14" x2="50" y2="24" stroke="#b9a6c9" strokeWidth="3" />
      <circle cx="50" cy="11" r="5" fill="#ee6c9c" />
      <rect x="17" y="38" width="8" height="16" rx="4" fill="#d9c8e6" />
      <rect x="75" y="38" width="8" height="16" rx="4" fill="#d9c8e6" />
      <rect x="22" y="22" width="56" height="44" rx="18" fill="url(#rbHead)" stroke="#e3d3ec" strokeWidth="1.5" />
      <rect x="29" y="31" width="42" height="26" rx="12" fill="#2b2547" />
      <path d="M38 46 q4 -6 8 0" stroke="#7fe3ff" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M54 46 q4 -6 8 0" stroke="#7fe3ff" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M32 72 h36 a6 6 0 0 1 6 6 v12 H26 v-12 a6 6 0 0 1 6 -6z" fill="url(#rbHead)" stroke="#e3d3ec" strokeWidth="1.5" />
      <path d="M50 86 s-6 -3.6 -6 -7.6 a3.2 3.2 0 0 1 6 -1.6 a3.2 3.2 0 0 1 6 1.6 c0 4 -6 7.6 -6 7.6z" fill="#ee6c9c" />
    </svg>
  );
}

/* ---------- self-care card illustrations ---------- */

export function FoodArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <g fill="#e8457c">
        <rect x="16" y="6" width="3" height="16" rx="1.5" />
        <rect x="21" y="6" width="3" height="16" rx="1.5" />
        <rect x="26" y="6" width="3" height="16" rx="1.5" />
        <path d="M15 20 h15 v4 a7.5 7.5 0 0 1 -5 7 v24 a2.5 2.5 0 0 1 -5 0 v-24 a7.5 7.5 0 0 1 -5 -7z" />
        <ellipse cx="44" cy="17" rx="8" ry="11" />
        <rect x="41.5" y="26" width="5" height="31" rx="2.5" />
      </g>
      <ellipse cx="41" cy="13" rx="2.2" ry="4" fill="#fff" opacity="0.45" />
    </svg>
  );
}

export function StethoscopeArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <path d="M16 8 v14 a10 10 0 0 0 20 0 V8" stroke="#3f8fd8" strokeWidth="4" fill="none" strokeLinecap="round" />
      <circle cx="16" cy="8" r="3" fill="#2f6fb0" />
      <circle cx="36" cy="8" r="3" fill="#2f6fb0" />
      <path d="M26 32 v8 a10 10 0 0 0 20 0 v-6" stroke="#3f8fd8" strokeWidth="4" fill="none" strokeLinecap="round" />
      <circle cx="46" cy="28" r="8" fill="#e8457c" />
      <circle cx="46" cy="28" r="3.5" fill="#fff" />
    </svg>
  );
}

export function LotusArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      {[-60, 60, -30, 30, 0].map((a, i) => (
        <path
          key={i}
          d="M32 50 C24 40 24 24 32 12 C40 24 40 40 32 50Z"
          fill={i < 2 ? "#f6b3cb" : i < 4 ? "#ee86ab" : "#e0508a"}
          transform={`rotate(${a} 32 50)`}
        />
      ))}
      <path d="M32 50 C20 54 10 52 4 46 C14 43 24 45 32 50Z M32 50 C44 54 54 52 60 46 C50 43 40 45 32 50Z" fill="#f2a0bf" />
    </svg>
  );
}

export function SmileyArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <defs>
        <radialGradient id="smile" cx="0.38" cy="0.32" r="0.75">
          <stop offset="0" stopColor="#ffe680" />
          <stop offset="1" stopColor="#f7b500" />
        </radialGradient>
      </defs>
      <circle cx="32" cy="32" r="24" fill="url(#smile)" />
      <ellipse cx="24" cy="27" rx="3" ry="4" fill="#5b3a00" />
      <ellipse cx="40" cy="27" rx="3" ry="4" fill="#5b3a00" />
      <path d="M21 37 q11 11 22 0" stroke="#5b3a00" strokeWidth="3.4" fill="none" strokeLinecap="round" />
      <circle cx="18" cy="36" r="3.5" fill="#ff9aa8" opacity="0.6" />
      <circle cx="46" cy="36" r="3.5" fill="#ff9aa8" opacity="0.6" />
    </svg>
  );
}

export function SunriseArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <circle cx="32" cy="40" r="14" fill="#ffb36b" />
      {[-70, -35, 0, 35, 70].map((a) => (
        <rect key={a} x="30.5" y="12" width="3" height="9" rx="1.5" fill="#ff9a4d" transform={`rotate(${a} 32 40)`} />
      ))}
      <rect x="6" y="40" width="52" height="16" fill="#fde7ef" />
      <path d="M8 44 h48 M14 50 h36" stroke="#ee86ab" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export function StretchArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <circle cx="32" cy="12" r="6" fill="#e8457c" />
      <path d="M32 20 v18 M32 24 L16 14 M32 24 L48 14 M32 38 L20 54 M32 38 L44 54" stroke="#ee86ab" strokeWidth="5" strokeLinecap="round" fill="none" />
      <ellipse cx="32" cy="57" rx="20" ry="3" fill="#fbd6e3" />
    </svg>
  );
}

export function WorkoutArt() {
  return (
    <svg viewBox="0 0 64 64" className="art" aria-hidden="true">
      <rect x="10" y="29" width="44" height="6" rx="3" fill="#b9a6c9" />
      <rect x="12" y="18" width="8" height="28" rx="3" fill="#e8457c" />
      <rect x="44" y="18" width="8" height="28" rx="3" fill="#e8457c" />
      <rect x="5" y="23" width="6" height="18" rx="2.5" fill="#ee86ab" />
      <rect x="53" y="23" width="6" height="18" rx="2.5" fill="#ee86ab" />
    </svg>
  );
}

export function TeaArt() {
  return (
    <svg viewBox="0 0 80 80" className="art" aria-hidden="true">
      <path d="M30 18 c-4 -6 4 -8 0 -14 M40 18 c-4 -6 4 -8 0 -14" stroke="#e6b8c8" strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <path d="M14 26 h44 v18 a20 20 0 0 1 -20 20 h-4 a20 20 0 0 1 -20 -20z" fill="#fff" stroke="#f3c3d4" strokeWidth="2" />
      <ellipse cx="36" cy="27" rx="22" ry="5" fill="#a8693f" />
      <path d="M58 32 h4 a8 8 0 0 1 0 16 h-5" stroke="#f3c3d4" strokeWidth="4" fill="none" />
      <ellipse cx="36" cy="70" rx="28" ry="5" fill="#fbd6e3" />
    </svg>
  );
}
