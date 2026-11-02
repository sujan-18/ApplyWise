
from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application
from app.schemas.application import ApplicationResponse
from app.routers import auth, applications


app = FastAPI(
    title="ApplyWise API",
    description="Backend API for managing internship applications",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(applications.router)



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

@app.get(
    "/applications",
    response_model=list[ApplicationResponse]
)
def get_applications(
    db: Annotated[Session, Depends(get_db)]
):
    statement = select(Application)

    applications = db.scalars(statement).all()

    return applications