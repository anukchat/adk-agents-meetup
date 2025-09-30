from typing import List, Optional
from pydantic import BaseModel
from datetime import date


class WorkExperience(BaseModel):
    job_title: str
    company: str
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]  # None or "present" for ongoing
    description: Optional[str]  # responsibilities, achievements


class Education(BaseModel):
    degree: str
    institution: str
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    grade: Optional[str]  # GPA, percentage, honors


class Certification(BaseModel):
    name: str
    issuer: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]
    credential_id: Optional[str]
    credential_url: Optional[str]


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    link: Optional[str]


class LanguageProficiency(BaseModel):
    language: str
    proficiency: str  # e.g., "Native", "Fluent", "Intermediate"


class CVScreenerOutput(BaseModel):
    # Identity & Contact
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    website: Optional[str]
    address: Optional[str]

    # Summary
    professional_summary: Optional[str]

    # Key Sections
    skills: List[str]
    work_experience: List[WorkExperience]
    education: List[Education]
    certifications: Optional[List[Certification]]
    projects: Optional[List[Project]]
    languages: Optional[List[LanguageProficiency]]

    # Meta
    total_experience_years: Optional[float]
    preferred_roles: Optional[List[str]]
    preferred_locations: Optional[List[str]]
    availability: Optional[str]  # e.g., "Immediate", "2 months notice"


class JobPosting(BaseModel):
    job_title: str
    company: str
    location: Optional[str]
    job_description: str
    requirements: List[str]
    application_link: Optional[str]
    posted_date: Optional[str]
    employment_type: Optional[str]  # e.g., "Full-time", "Part-time", "Contract"