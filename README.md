# HerRhythm

Menstrual and wellness companion: a FastAPI backend (`backend/`) and a React web app (`web/`).
The old Streamlit frontend (`frontend/`) is no longer used.

## Run for development

Terminal 1 – backend (from this folder):

```
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

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
npm run build
cd ..
uvicorn backend.main:app --port 8000
```

Open http://localhost:8000. The backend serves the built app from `web/dist`.

## App flow

Splash (HerRhythm logo) → Welcome / Get Started → Log in or Sign up → Home.
Bottom navigation: Home, Calendar, + (Track), Chatbot, Profile.
