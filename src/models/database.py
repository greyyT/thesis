"""Database models using SQLModel."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Session, create_engine, Relationship, Column, JSON
from sqlalchemy import func, event
from sqlalchemy.engine import Engine


class Job(SQLModel, table=True):
    """Job posting model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    requirements: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    job_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    screening_results: List["ScreeningResult"] = Relationship(back_populates="job")


class Candidate(SQLModel, table=True):
    """Candidate model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    phone: Optional[str] = None
    current_stage: str = Field(default="sourcing")
    stage_history: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    candidate_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    resumes: List["Resume"] = Relationship(back_populates="candidate")
    interview_feedback: List["InterviewFeedback"] = Relationship(
        back_populates="candidate",
        cascade_delete=True
    )


class Resume(SQLModel, table=True):
    """Resume model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    content: str
    parsed_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    file_path: Optional[str] = None
    embedding_id: Optional[str] = None  # Reference to vector store
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    candidate_fk: Optional[int] = Field(default=None, foreign_key="candidate.id")
    
    # Relationships
    candidate: Optional[Candidate] = Relationship(back_populates="resumes")
    screening_results: List["ScreeningResult"] = Relationship(back_populates="resume")


class ScreeningResult(SQLModel, table=True):
    """Screening result model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    resume_id: int = Field(foreign_key="resume.id")
    match_score: float = Field(ge=0.0, le=1.0)
    skill_matches: List[str] = Field(default=[], sa_column=Column(JSON))
    skill_gaps: List[str] = Field(default=[], sa_column=Column(JSON))
    reasoning: Optional[str] = None
    recommendation: str  # "proceed", "reject", "review"
    bias_check: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    job: Job = Relationship(back_populates="screening_results")
    resume: Resume = Relationship(back_populates="screening_results")


class InterviewFeedback(SQLModel, table=True):
    """Interview feedback model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidate.id")
    interviewer_id: str
    interview_type: str  # "technical", "behavioral", "cultural"
    ratings: Dict[str, int] = Field(default={}, sa_column=Column(JSON))
    notes: Optional[str] = None
    recommendation: str  # "hire", "no_hire", "maybe"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    candidate: Candidate = Relationship(back_populates="interview_feedback")


class AuditLog(SQLModel, table=True):
    """Audit log model for tracking system events."""
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(index=True)
    user_id: str = Field(index=True)
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    changes: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


def create_all_tables(engine):
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session(database_url: str) -> Session:
    """Get database session."""
    engine = create_engine(database_url)
    return Session(engine)


# Event listeners for automatic timestamp updates
@event.listens_for(Job, "before_update")
def update_job_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(Candidate, "before_update")
def update_candidate_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)