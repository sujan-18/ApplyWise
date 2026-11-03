
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.database import engine

from app.routers import auth, applications, resume, ai
from fastapi.middleware.cors import CORSMiddleware

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "Frontend"
FRONTEND_SRC = FRONTEND_DIR / "src"


app = FastAPI(
    title="ApplyWise API",
    description="Backend API for managing internship applications",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(resume.router)
app.include_router(ai.router)



@app.get("/")
def root():
    return {
        "message": "Welcome to ApplyWise API",
        "status": "running",
    }


@app.get("/health/database")
def check_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar_one(),
    }


app.mount("/app", StaticFiles(directory=FRONTEND_SRC, html=True), name="frontend")

