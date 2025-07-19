"""Global test configuration and fixtures."""
import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import numpy as np

# Set test environment
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"

# Add src to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration for testing."""
    return {
        "openai_api_key": "test-key",
        "database_url": "postgresql://test:test@localhost/test",
        "milvus_lite_file": "./test_milvus.db",
        "milvus_collection_name": "test_embeddings",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_password": "",
        "embedding_dimension": 1536,
        "hitl_confidence_threshold": 0.85,
        "log_level": "DEBUG",
        "testing": True,
        "enable_bias_detection": True,
        "enable_transferable_skills": True,
        "enable_audit_logging": True,
    }

@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """Senior Python Developer
    
    Requirements:
    - 5+ years of Python development experience
    - Strong knowledge of FastAPI, Django, or Flask
    - Experience with microservices architecture
    - Understanding of ML/AI concepts
    - AWS or cloud platform experience
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Open source contributions
    - Experience with Docker and Kubernetes
    - Knowledge of React or Vue.js
    """

@pytest.fixture
def sample_resume():
    """Sample resume for testing."""
    return """John Doe
    Email: john.doe@email.com | GitHub: github.com/johndoe
    
    SUMMARY
    Experienced software engineer with 6 years building scalable web applications.
    Self-taught programmer who transitioned from data analysis to full-stack development.
    
    SKILLS
    Programming: Python, JavaScript, SQL
    Frameworks: FastAPI, Express.js, React
    Tools: Docker, Git, Jenkins, AWS EC2/S3/Lambda
    Concepts: RESTful APIs, Microservices, Machine Learning basics
    
    EXPERIENCE
    Senior Developer | TechStartup Inc. | 2021-Present
    - Architected microservices platform handling 1M+ daily requests
    - Reduced API response time by 60% through optimization
    - Mentored team of 3 junior developers
    
    Full Stack Developer | DataCorp | 2019-2021  
    - Built customer analytics dashboard using Python/React
    - Implemented ML models for customer churn prediction
    - Deployed applications on AWS with 99.9% uptime
    
    Data Analyst | FinanceGlobal | 2018-2019
    - Automated reporting with Python scripts
    - Created data pipelines processing 500GB+ daily
    
    EDUCATION
    Data Science Bootcamp | DataCamp | 2018
    B.A. Economics | State University | 2017
    
    PROJECTS
    - Contributed to popular open-source Python ORM (500+ stars)
    - Built personal finance tracker with FastAPI backend
    """

@pytest.fixture
def mock_embedding():
    """Mock 1536-dimensional embedding."""
    return np.random.rand(1536)

@pytest.fixture
def mock_job_factory():
    """Factory for creating test job descriptions."""
    def _factory(**kwargs):
        defaults = {
            "title": "Senior Python Developer",
            "description": "We need an experienced Python developer...",
            "requirements": {
                "technical_skills": ["Python", "FastAPI", "Docker"],
                "experience_years": {"minimum": 5, "preferred": 7},
                "education": {"level": "Bachelor's", "fields": ["Computer Science"]},
                "soft_skills": ["Communication", "Teamwork"],
                "domain": ["Web Development"],
                "nice_to_have": ["Kubernetes", "AWS"]
            }
        }
        defaults.update(kwargs)
        return defaults
    return _factory

@pytest.fixture
def mock_resume_factory():
    """Factory for creating test resumes."""
    def _factory(**kwargs):
        defaults = {
            "name": "John Doe",
            "email": "john@example.com",
            "text": """John Doe - Senior Software Engineer
            6 years Python development experience
            Skills: Python, FastAPI, Docker, PostgreSQL
            Education: BS Computer Science""",
            "skills": {
                "technical": ["Python", "FastAPI", "Docker"],
                "soft": ["Problem Solving", "Communication"]
            },
            "experience_years": 6.0,
            "education": [{
                "degree": "Bachelor's",
                "field": "Computer Science",
                "institution": "State University",
                "year": "2017"
            }]
        }
        defaults.update(kwargs)
        return defaults
    return _factory

# Mock external services
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = Mock()
    client.embeddings = Mock()
    client.embeddings.create = AsyncMock(
        return_value=Mock(
            data=[Mock(embedding=np.random.rand(1536).tolist())]
        )
    )
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    return client

@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    client = Mock()
    client.ping = AsyncMock(return_value=True)
    client.hset = AsyncMock()
    client.hget = AsyncMock()
    client.hgetall = AsyncMock(return_value={})
    client.zadd = AsyncMock()
    client.zrevrange = AsyncMock(return_value=[])
    client.publish = AsyncMock()
    client.hincrby = AsyncMock()
    return client

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
TEST_DATA_DIR.mkdir(exist_ok=True)