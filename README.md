# HerRhythm

Menstrual and wellness companion: a FastAPI backend (`backend/`) and a React web app (`web/`).
The old Streamlit frontend (`frontend/`) is no longer used.

## Run for development

Terminal 1 – backend (from this folder):

```
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

`requirements.txt` contains the FastAPI runtime dependencies. The complete
dependency set for the archived Streamlit frontend is retained in
`requirements-legacy.txt`; install that file only if you need to run the old
Streamlit frontend (`pip install -r requirements-legacy.txt`).

Terminal 2 – web app:

```
cd web
npm install
npm run dev
```

Open http://localhost:5173

### Enable HerBot

The chatbot requires a Gemini API key. Copy `.env.example` to `.env`, replace
the placeholder with your own key, and restart FastAPI:

```
Copy-Item .env.example .env
notepad .env
uvicorn backend.main:app --reload --port 8000
```

Never commit `.env`; it is ignored by Git.

### Enable email reminders

Add these values to the project-root `.env` file, then restart FastAPI:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your Gmail address
SMTP_PASSWORD=your 16-character Google app password
SMTP_FROM=your Gmail address
```

For Gmail, enable 2-Step Verification and create an **App password** in your
Google Account. Do not use your regular Gmail password. Other providers need
their SMTP host and port. If port 587 is blocked, use `SMTP_PORT=465`; the
application will use Gmail's direct SSL connection automatically.

## Seed demo data

From the project root, run:

```
python seed_demo.py
```

This creates or reuses the isolated demo account `demo@herrhythm.local` with
password `demo1234`, then inserts six months of cycles, daily wellness logs,
symptoms, moods, and calendar tags. It is safe to run repeatedly; it does not
delete or overwrite real user data.

## Run as one server

```
cd web
$env:VITE_API_URL = "/"
npm run build
cd ..
uvicorn backend.main:app --port 8000
```

Open http://localhost:8000. The backend serves the built app from `web/dist`.

## Deploy frontend to Vercel and backend to Render

Deploy the repository to Vercel and set **Root Directory** to `web`. Set
**Framework Preset** to **Vite** (not FastAPI), **Install Command** to
`npm ci`, **Build Command** to `npm run build`, and **Output Directory** to
`dist`. The `web/vercel.json` contains the same frontend-only settings and
SPA rewrite. The root `vercel.json` is also static-only for deployments whose
Root Directory is the repository root; neither file registers a Python
function.

Deploy the backend and managed PostgreSQL database using the included
`render.yaml` Blueprint. The Render service uses:

```
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

In the Render service settings, set:

- `FRONTEND_ORIGINS` to the exact Vercel production origin, for example
  `https://your-project.vercel.app` (no trailing slash). Add additional
  preview/custom origins as comma-separated exact origins when needed.
- `GEMINI_API_KEY` to your Gemini key.
- SMTP settings if email reminders are enabled.

After Render deploys, set the Vercel environment variable `VITE_API_URL` to
the Render service URL (for example `https://herrhythm-api.onrender.com`, with
no trailing slash) for Production, Preview, and Development as applicable,
then redeploy the frontend. Production API requests now fail with a clear
configuration error rather than falling back to the Vercel frontend origin if
this variable is missing. In the Vercel project, also confirm the Production
Branch is `main` and redeploy the latest commit with the build cache cleared.

`DATABASE_URL` is supplied by Render from the managed PostgreSQL database.
Local development continues to default to `sqlite:///./cycle_ai.db`. Existing
local SQLite records are not automatically copied to the production database;
import them separately if they need to be retained.

For local development, set `JWT_SECRET` to a long random value in `.env`.
Render generates this value automatically. Do not commit `.env` or paste
production secrets into source files.

## App flow

Splash (HerRhythm logo) → Welcome / Get Started → Log in or Sign up → Home.
Bottom navigation: Home, Calendar, + (Track), Chatbot, Profile.
