
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class Skills(BaseModel):
    technical: list[str] = Field(
        description="Technical skills found in the resume"
    )
    soft: list[str] = Field(
        description="Soft skills found in the resume"
    )


class Education(BaseModel):
    degree: str
    institution: str
    expected_graduation: str


class Project(BaseModel):
    name: str
    description: str
    technologies: list[str]


class ResumeAnalysis(BaseModel):
    candidate_name: str
    email: str
    phone: str
    skills: Skills
    education: list[Education]
    work_experience: list[str]
    projects: list[Project]
    recommended_internship_roles: list[str]
    recommended_job_roles: list[str]
    missing_skills: list[str]
    career_suggestions: list[str]


class ResumeAnalysisResponse(BaseModel):
    message: str
    user_id: int
    filename: str
    analysis: ResumeAnalysis

class SavedResumeAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    analysis: ResumeAnalysis
    created_at: datetime