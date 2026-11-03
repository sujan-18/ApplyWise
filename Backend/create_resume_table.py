
from app.database import Base, engine

# Import all models so SQLAlchemy knows about them
from app.models import User, Application, ResumeAnalysis


# Create only tables that do not already exist
Base.metadata.create_all(bind=engine, tables=[
    ResumeAnalysis.__table__
])

print("Resume analyses table created successfully!")
