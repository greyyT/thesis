"""Unit tests for database models."""
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from sqlmodel import Session, create_engine, SQLModel, select
from sqlalchemy.pool import StaticPool
import time

from models.database import (
    Job, Resume, Candidate, ScreeningResult,
    InterviewFeedback, AuditLog, create_all_tables
)


class TestDatabaseModels:
    """Test suite for database models."""
    
    @pytest.fixture
    def session(self):
        """Create test database session."""
        # Use in-memory SQLite for tests
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            yield session
    
    def test_job_creation(self, session):
        """Test: Job model should store job information correctly."""
        # Arrange
        job_data = {
            "title": "Senior Python Developer",
            "description": "We need a Python expert...",
            "requirements": {
                "skills": ["Python", "FastAPI"],
                "experience": 5
            }
        }
        
        # Act
        job = Job(**job_data)
        session.add(job)
        session.commit()
        
        # Assert
        assert job.id is not None
        assert job.title == "Senior Python Developer"
        assert job.requirements["skills"] == ["Python", "FastAPI"]
        assert job.created_at is not None
        assert job.updated_at is not None
    
    def test_resume_creation(self, session):
        """Test: Resume model should store candidate information."""
        # Arrange
        resume_data = {
            "candidate_id": "test-candidate-123",
            "content": "John Doe - Senior Developer...",
            "parsed_data": {
                "name": "John Doe",
                "skills": ["Python", "JavaScript"],
                "experience_years": 5.0
            },
            "file_path": "/data/resumes/john_doe.pdf"
        }
        
        # Act
        resume = Resume(**resume_data)
        session.add(resume)
        session.commit()
        
        # Assert
        assert resume.id is not None
        assert resume.candidate_id == "test-candidate-123"
        assert resume.parsed_data["skills"] == ["Python", "JavaScript"]
        assert resume.file_path == "/data/resumes/john_doe.pdf"
    
    def test_candidate_creation(self, session):
        """Test: Candidate model should track recruitment progress."""
        # Arrange
        candidate_data = {
            "email": "john.doe@example.com",
            "name": "John Doe",
            "phone": "+1234567890",
            "current_stage": "screening",
            "stage_history": [{
                "stage": "sourcing",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": "passed"
            }]
        }
        
        # Act
        candidate = Candidate(**candidate_data)
        session.add(candidate)
        session.commit()
        
        # Assert
        assert candidate.id is not None
        assert candidate.email == "john.doe@example.com"
        assert candidate.current_stage == "screening"
        assert len(candidate.stage_history) == 1
        assert candidate.stage_history[0]["stage"] == "sourcing"
    
    def test_screening_result_creation(self, session):
        """Test: ScreeningResult model should store evaluation data."""
        # Arrange
        # First create related job and resume
        job = Job(
            title="Python Developer",
            description="Python role",
            requirements={"skills": ["Python"]}
        )
        resume = Resume(
            candidate_id="test-123",
            content="Resume content",
            parsed_data={"skills": ["Python"]}
        )
        session.add_all([job, resume])
        session.commit()
        
        screening_data = {
            "job_id": job.id,
            "resume_id": resume.id,
            "match_score": 0.85,
            "skill_matches": ["Python"],
            "skill_gaps": ["Docker"],
            "reasoning": "Strong Python experience",
            "recommendation": "proceed",
            "bias_check": {
                "flags": [],
                "score": 0.95
            }
        }
        
        # Act
        screening = ScreeningResult(**screening_data)
        session.add(screening)
        session.commit()
        
        # Assert
        assert screening.id is not None
        assert screening.match_score == 0.85
        assert screening.skill_matches == ["Python"]
        assert screening.recommendation == "proceed"
        assert screening.bias_check["score"] == 0.95
    
    def test_interview_feedback_creation(self, session):
        """Test: InterviewFeedback model should store interview data."""
        # Arrange
        # Create candidate first
        candidate = Candidate(
            email="john@example.com",
            name="John Doe",
            current_stage="interview"
        )
        session.add(candidate)
        session.commit()
        
        feedback_data = {
            "candidate_id": candidate.id,
            "interviewer_id": "interviewer-123",
            "interview_type": "technical",
            "ratings": {
                "technical_skills": 4,
                "communication": 5,
                "problem_solving": 4
            },
            "notes": "Strong technical skills",
            "recommendation": "hire"
        }
        
        # Act
        feedback = InterviewFeedback(**feedback_data)
        session.add(feedback)
        session.commit()
        
        # Assert
        assert feedback.id is not None
        assert feedback.interview_type == "technical"
        assert feedback.ratings["technical_skills"] == 4
        assert feedback.recommendation == "hire"
    
    def test_audit_log_creation(self, session):
        """Test: AuditLog model should track system events."""
        # Arrange
        audit_data = {
            "event_type": "resume_screened",
            "user_id": "system",
            "entity_type": "screening_result",
            "entity_id": "screening-123",
            "changes": {
                "action": "create",
                "score": 0.85
            },
            "ip_address": "127.0.0.1"
        }
        
        # Act
        audit = AuditLog(**audit_data)
        session.add(audit)
        session.commit()
        
        # Assert
        assert audit.id is not None
        assert audit.event_type == "resume_screened"
        assert audit.entity_type == "screening_result"
        assert audit.changes["score"] == 0.85
        assert audit.timestamp is not None
    
    def test_relationships(self, session):
        """Test: Model relationships should work correctly."""
        # Arrange
        job = Job(
            title="Full Stack Developer",
            description="Full stack role",
            requirements={"skills": ["Python", "React"]}
        )
        
        candidate = Candidate(
            email="jane@example.com",
            name="Jane Smith",
            current_stage="sourcing"
        )
        
        resume = Resume(
            candidate_id="jane-123",
            content="Jane's resume",
            parsed_data={"name": "Jane Smith"},
            candidate=candidate  # Set relationship
        )
        
        session.add_all([job, candidate, resume])
        session.commit()
        
        screening = ScreeningResult(
            job_id=job.id,
            resume_id=resume.id,
            match_score=0.90,
            skill_matches=["Python"],
            recommendation="proceed"
        )
        
        session.add(screening)
        session.commit()
        
        # Act - Test relationships
        session.refresh(screening)
        
        # Assert
        assert screening.job.title == "Full Stack Developer"
        assert screening.resume.candidate_id == "jane-123"
        assert screening.resume.candidate.name == "Jane Smith"
    
    def test_json_field_handling(self, session):
        """Test: JSON fields should handle complex data correctly."""
        # Arrange
        job = Job(
            title="ML Engineer",
            description="ML role",
            requirements={
                "skills": {
                    "required": ["Python", "TensorFlow"],
                    "preferred": ["PyTorch", "MLflow"]
                },
                "experience": {
                    "minimum": 3,
                    "preferred": 5
                },
                "education": ["MS CS", "PhD ML"]
            },
            job_metadata={
                "department": "AI Research",
                "team_size": 10,
                "remote": True
            }
        )
        
        # Act
        session.add(job)
        session.commit()
        session.refresh(job)
        
        # Assert
        assert job.requirements["skills"]["required"] == ["Python", "TensorFlow"]
        assert job.requirements["experience"]["minimum"] == 3
        assert job.job_metadata["remote"] is True
    
    def test_timestamp_fields(self, session):
        """Test: Timestamp fields should update correctly."""
        # Arrange
        job = Job(
            title="DevOps Engineer",
            description="DevOps role",
            requirements={"skills": ["Kubernetes"]}
        )
        
        # Act - Create
        session.add(job)
        session.commit()
        created_time = job.created_at
        updated_time = job.updated_at
        
        # Act - Update (add small delay to ensure timestamp difference)
        time.sleep(0.01)
        job.title = "Senior DevOps Engineer"
        session.commit()
        session.refresh(job)
        
        # Assert
        assert job.created_at == created_time  # Should not change
        assert job.updated_at > updated_time  # Should be updated
    
    def test_cascade_operations(self, session):
        """Test: Cascade operations should work correctly."""
        # Arrange
        candidate = Candidate(
            email="test@example.com",
            name="Test User",
            current_stage="screening"
        )
        
        resume = Resume(
            candidate_id="test-user",
            content="Test resume",
            parsed_data={},
            candidate=candidate
        )
        
        session.add_all([candidate, resume])
        session.commit()
        
        feedback = InterviewFeedback(
            candidate_id=candidate.id,
            interviewer_id="int-123",
            interview_type="phone",
            ratings={"overall": 4},
            recommendation="proceed"
        )
        
        session.add(feedback)
        session.commit()
        
        # Act - Delete candidate (should cascade to feedback)
        session.delete(candidate)
        session.commit()
        
        # Assert - Using SQLModel's select instead of query
        statement = select(InterviewFeedback).where(
            InterviewFeedback.candidate_id == candidate.id
        )
        result = session.exec(statement).first()
        assert result is None