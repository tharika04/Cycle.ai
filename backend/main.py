
import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from backend.database import Base, engine
from backend import models, day_models
import backend.daylog_model  # noqa: F401 (registers day_tags table)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


def ensure_columns():
    inspector = inspect(engine)

    if "chat_history" in inspector.get_table_names():
        cols = [
            c["name"]
            for c in inspector.get_columns("chat_history")
        ]

        if "conversation_id" not in cols:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE chat_history "
                        "ADD COLUMN conversation_id VARCHAR"
                    )
                )

    daily_cols = {c["name"] for c in inspector.get_columns("daily_logs")}
    if "stress" not in daily_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE daily_logs ADD COLUMN stress INTEGER"))


ensure_columns()


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(title="HerRhythm")


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.5:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://192.168.1.5:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://192.168.1.5:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ROUTER REGISTRATION
# --------------------------------------------------

ROUTERS = [
    "auth_router",
    "cycles",
    "symptoms",
    "predict",
    "plan",
    "chat",
    "account",
    "daily",
    "wellness",
    "mealplan",
    "dayentries",
    "daylog",
    "routines",
]

for name in ROUTERS:
    path = "backend.routers." + name

    try:
        module = importlib.import_module(path)

    except ModuleNotFoundError as e:
        if e.name == path:
            continue
        raise

    app.include_router(module.router)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "running"}


# --------------------------------------------------
# FRONTEND STATIC FILES
# --------------------------------------------------

DIST = (
    Path(__file__).resolve().parent.parent
    / "web"
    / "dist"
)

if DIST.is_dir():

    app.mount(
        "/assets",
        StaticFiles(directory=DIST / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):

        file = DIST / full_path

        if (
            full_path
            and file.is_file()
            and DIST in file.resolve().parents
        ):
            return FileResponse(file)

        return FileResponse(DIST / "index.html")

else:

    @app.get("/")
    def root():
        return {"status": "running"}
