# Test-Driven POC Implementation Guide

## Overview

This document follows Test-Driven Development (TDD) principles to build a robust Multi-Agent Recruitment System POC. Each component is developed using the Red-Green-Refactor cycle:

1. 🔴 **Red**: Write a failing test
2. 🟢 **Green**: Write minimal code to pass
3. 🔵 **Refactor**: Improve the code

This approach ensures easier debugging, better code coverage, and more maintainable implementation.

## TDD Development Principles

### Why Test-First?
1. **Clearer Requirements**: Tests define exactly what each component should do
2. **Easier Debugging**: Isolated tests pinpoint failures quickly
3. **Better Design**: TDD forces modular, testable code
4. **Living Documentation**: Tests show how to use each component
5. **Confidence**: Refactoring is safe with comprehensive tests

### Agent Functionalities to Test
We'll build a **Unified Recruitment Agent** with test coverage for:
- **Supervisor**: Job requirement decomposition
- **Sourcing**: Resume parsing and structuring
- **Screening**: Semantic matching and scoring
- **Critic**: Bias detection and adjustments
- **HITL**: Confidence calculation and routing
- **Data-Steward**: Audit logging and compliance

### Testing Strategy
- Unit tests for each component
- Integration tests for component interactions
- End-to-end tests for complete workflows
- Performance tests for bottlenecks

## Technology Stack (Simplified)

```python
# Core Dependencies
- Python 3.12+
- pytest (test framework)
- pytest-asyncio (async testing)
- pytest-mock (mocking)
- LlamaIndex (multi-agent framework)
- Chainlit (chat interface)
- PostgreSQL (structured data only)
- Milvus Lite (local vector embeddings)
- Redis (state management)
```

## Test-First Development Guide

### Setting Up Testing Environment

```bash
# Create test structure
mkdir -p tests/{unit,integration,fixtures}
touch tests/conftest.py

# Install testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### Test Configuration (tests/conftest.py)

```python
import pytest
import asyncio
import os
from unittest.mock import MagicMock
from typing import Dict, Any

# Test environment setup
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"

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
        "redis_host": "localhost",
        "redis_port": 6379,
        "embedding_dimension": 1536,
        "hitl_confidence_threshold": 0.85
    }

@pytest.fixture
def sample_job_description():
    return """Senior Python Developer
    - 5+ years Python experience
    - FastAPI, Docker experience
    - Strong communication skills"""

@pytest.fixture
def sample_resume():
    return """John Doe
    Python Developer - 6 years experience
    Skills: Python, FastAPI, Docker, REST APIs
    Experience: Built microservices handling 1M requests/day"""

@pytest.fixture
def mock_embedding():
    """Mock 1536-dim embedding."""
    return np.random.rand(1536)
```

### Test Utilities (tests/test_utils.py)

```python
import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def time_it(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def assert_between(value: float, min_val: float, max_val: float, name: str = "value"):
    """Assert value is within range."""
    assert min_val <= value <= max_val, f"{name} {value} not in [{min_val}, {max_val}]"

class TestContext:
    """Context manager for test isolation."""
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            logger.error(f"Test failed after {duration:.2f}s: {exc_val}")
        else:
            logger.info(f"Test passed in {duration:.2f}s")
```

### TDD Workflow Example

```python
# Step 1: Write the test first (RED)
def test_skill_normalization():
    ontology = SkillOntologyService()
    assert ontology.normalize_skill("ML") == "machine_learning"
    assert ontology.normalize_skill("JS") == "javascript"

# Step 2: Run test - it fails (no implementation)
# $ pytest tests/test_skill_ontology.py::test_skill_normalization

# Step 3: Write minimal code to pass (GREEN)
class SkillOntologyService:
    def normalize_skill(self, skill: str) -> str:
        mappings = {"ML": "machine_learning", "JS": "javascript"}
        return mappings.get(skill, skill)

# Step 4: Test passes!
# Step 5: Refactor if needed (BLUE)
```

## Project Structure

```
recruitment-poc/
├── .env.example                    # Environment variables template
├── docker-compose.yml              # Local development services
├── requirements.txt                # Python dependencies
├── README.md                       # Quick start guide
├── src/
│   ├── main.py                     # Chainlit app entry point
│   ├── config.py                   # Configuration management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── unified_agent.py        # Main UnifiedRecruitmentAgent
│   │   └── prompts.py              # Agent prompt templates
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic/SQLModel schemas
│   │   └── database.py             # Database models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py           # LlamaIndex embedding service
│   │   ├── vector_store.py         # Milvus Lite operations
│   │   ├── redis_cache.py          # Redis operations
│   │   └── bias_detector.py        # Bias detection logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── skill_ontology.py       # Skill normalization & aliases
│   │   └── audit_logger.py         # Logging utilities
│   └── ui/
│       ├── __init__.py
│       └── chainlit_app.py         # Chainlit interface
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Test fixtures
│   ├── test_agent.py               # Agent tests
│   ├── test_matching.py            # Semantic matching tests
│   └── test_integration.py         # Integration tests
└── data/
    ├── skill_ontology.json         # Skill aliases and mappings
    └── sample_data.json            # Sample jobs and resumes
```

### Key Configuration Files

#### .env.example
```bash
# LLM Configuration
OPENAI_API_KEY=your_key_here
LLAMA_INDEX_CACHE_DIR=./cache

# Database (Neon.tech)
# Format: postgresql://[user]:[password]@[host]/[database]?sslmode=require
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/recruitment_poc?sslmode=require

# Cache & State
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CHANNEL=hitl_queue

# Application
HITL_CONFIDENCE_THRESHOLD=0.85
LOG_LEVEL=INFO
EMBEDDING_DIMENSION=1536  # for text-embedding-3-small

# Milvus Lite Configuration
MILVUS_LITE_FILE=./milvus_lite.db  # Local file storage
MILVUS_COLLECTION_NAME=recruitment_embeddings
```

#### docker-compose.yml
```yaml
version: '3.9'
services:
  # Only Redis needed locally - PostgreSQL hosted on Neon.tech
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis_data:
```

#### requirements.txt
```txt
# Core dependencies
python==3.12.*
chainlit==1.0.0
llama-index==0.10.19
redis==5.0.1
asyncpg==0.29.0
sqlmodel==0.0.14
pydantic==2.5.0

# PostgreSQL
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Milvus Lite (local vector database)
milvus-lite==2.4.0
pymilvus==2.4.0

# ML/NLP
numpy==1.26.0
scikit-learn==1.3.2
openai==1.12.0  # For embeddings and LLM

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
tenacity==8.2.3
loguru==0.7.2

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.0
ruff==0.1.9
mypy==1.7.1
```

## Component Development (TDD Approach)

### 1. Database Schema Component

#### Test Specification (tests/test_database.py)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from models.database import Job, Candidate, Evaluation, AuditLog

class TestDatabaseModels:
    """Test database models and constraints."""
    
    def test_job_creation(self, session):
        """Test: Job model should store job information correctly."""
        # Arrange
        job_data = {
            "title": "Senior Python Developer",
            "description": "We need a Python expert...",
            "requirements": {"skills": ["Python", "FastAPI"], "experience": 5}
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
    
    def test_candidate_email_uniqueness(self, session):
        """Test: Candidate emails must be unique."""
        # Arrange
        candidate1 = Candidate(name="John Doe", email="john@example.com")
        candidate2 = Candidate(name="Jane Doe", email="john@example.com")
        
        # Act & Assert
        session.add(candidate1)
        session.commit()
        
        session.add(candidate2)
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_evaluation_relationships(self, session):
        """Test: Evaluations should maintain referential integrity."""
        # Arrange
        job = Job(title="Test Job", description="Test")
        candidate = Candidate(name="Test User", email="test@example.com")
        session.add_all([job, candidate])
        session.commit()
        
        # Act
        evaluation = Evaluation(
            job_id=job.id,
            candidate_id=candidate.id,
            screening_score=0.85,
            critic_score=0.80,
            confidence=0.95
        )
        session.add(evaluation)
        session.commit()
        
        # Assert
        assert evaluation.job_id == job.id
        assert evaluation.candidate_id == candidate.id
        # Verify cascade delete protection
        with pytest.raises(IntegrityError):
            session.delete(job)
            session.commit()
```

#### Minimal Implementation (models/database.py)

```python
from sqlmodel import Field, SQLModel, JSON, Column
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class Job(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: str
    requirements: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Candidate(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(max_length=255)
    email: Optional[str] = Field(max_length=255, unique=True)
    resume_text: Optional[str]
    parsed_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Evaluation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(foreign_key="job.id")
    candidate_id: uuid.UUID = Field(foreign_key="candidate.id")
    screening_score: Optional[float]
    critic_score: Optional[float]
    confidence: Optional[float]
    needs_review: Optional[bool] = False
    bias_flags: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    decision: Optional[str] = Field(max_length=50)
    decision_reason: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: str = Field(max_length=255)
    agent_type: str = Field(max_length=50)
    action: str = Field(max_length=100)
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EmbeddingMetadata(SQLModel, table=True):
    __tablename__ = "embedding_metadata"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_type: str = Field(max_length=50)  # 'skill', 'job', 'candidate'
    entity_id: str = Field(max_length=255)
    milvus_id: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Debugging Tips
- **Common Issue**: Foreign key constraints fail
  - **Solution**: Ensure referenced records exist before creating relationships
  - **Debug**: Check with `session.query(Job).filter_by(id=job_id).first()`
- **Common Issue**: JSON fields not storing properly
  - **Solution**: Use SQLModel's JSON column type explicitly
  - **Debug**: Print `evaluation.bias_flags` after commit

### 2. Vector Store Service Component

#### Test Specification (tests/test_vector_store.py)

```python
import pytest
import numpy as np
from unittest.mock import Mock, patch
from services.vector_store import MilvusLiteStore

class TestMilvusLiteStore:
    """Test vector storage operations with Milvus Lite."""
    
    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create a test vector store with temporary file."""
        db_file = str(tmp_path / "test_milvus.db")
        store = MilvusLiteStore(db_file=db_file)
        store.initialize()
        yield store
        store.close()
    
    def test_initialization_creates_collection(self, vector_store):
        """Test: Vector store should create collection on initialization."""
        # Assert
        assert vector_store.collection is not None
        assert vector_store.collection.name == "recruitment_embeddings"
    
    def test_store_and_retrieve_skill_embedding(self, vector_store):
        """Test: Should store and retrieve skill embeddings correctly."""
        # Arrange
        skill_name = "python"
        embedding = np.random.rand(1536)
        
        # Act
        vector_store.store_skill_embedding(skill_name, embedding)
        similar_skills = vector_store.find_similar_skills(embedding, top_k=1)
        
        # Assert
        assert len(similar_skills) == 1
        assert similar_skills[0][0] == skill_name
        assert similar_skills[0][1] > 0.99  # Should be nearly identical
    
    def test_match_candidate_to_job(self, vector_store):
        """Test: Should match candidate skills to job requirements."""
        # Arrange
        job_id = "job_123"
        candidate_id = "cand_456"
        
        # Store job requirements
        job_embeddings = [
            {"text": "Python", "type": "skill", "embedding": np.random.rand(1536)},
            {"text": "FastAPI", "type": "skill", "embedding": np.random.rand(1536)}
        ]
        vector_store.store_job_embeddings(job_id, job_embeddings)
        
        # Store candidate skills
        candidate_embeddings = [
            {"skill": "Python", "embedding": job_embeddings[0]["embedding"]},  # Perfect match
            {"skill": "Django", "embedding": np.random.rand(1536)}  # Different skill
        ]
        vector_store.store_candidate_embeddings(candidate_id, candidate_embeddings)
        
        # Act
        matches = vector_store.match_candidate_to_job(job_id, candidate_id)
        
        # Assert
        assert "Python" in matches
        assert matches["Python"]["similarity"] > 0.99
        assert matches["Python"]["best_match"] == "Python"
    
    def test_duplicate_skill_updates_existing(self, vector_store):
        """Test: Storing duplicate skill should update, not create new."""
        # Arrange
        skill_name = "javascript"
        embedding1 = np.random.rand(1536)
        embedding2 = np.random.rand(1536)
        
        # Act
        vector_store.store_skill_embedding(skill_name, embedding1)
        vector_store.store_skill_embedding(skill_name, embedding2)
        
        # Search for both embeddings
        results1 = vector_store.find_similar_skills(embedding1, top_k=2)
        results2 = vector_store.find_similar_skills(embedding2, top_k=2)
        
        # Assert - only the second embedding should be found
        assert len(results2) >= 1
        assert results2[0][0] == skill_name
        # First embedding should not be the top match anymore
        assert len(results1) == 0 or results1[0][1] < 0.99

class TestVectorStoreEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_collection_search(self, vector_store):
        """Test: Searching empty collection should return empty results."""
        # Arrange
        random_embedding = np.random.rand(1536)
        
        # Act
        results = vector_store.find_similar_skills(random_embedding, top_k=5)
        
        # Assert
        assert results == []
    
    def test_invalid_embedding_dimension(self, vector_store):
        """Test: Should handle invalid embedding dimensions gracefully."""
        # Arrange
        wrong_dim_embedding = np.random.rand(512)  # Wrong dimension
        
        # Act & Assert
        with pytest.raises(Exception):  # Milvus will raise dimension mismatch
            vector_store.store_skill_embedding("test", wrong_dim_embedding)
```

#### Minimal Implementation (services/vector_store.py)

```python
# src/services/vector_store.py
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import json
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)

logger = logging.getLogger(__name__)

class MilvusLiteStore:
    """Milvus Lite local vector store for embeddings."""
    
    def __init__(self, db_file: str = "./milvus_lite.db", collection_name: str = "recruitment_embeddings", embedding_dim: int = 1536):
        self.db_file = db_file
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.collection = None
    
    def initialize(self):
        """Initialize Milvus Lite connection and create collection."""
        # Connect to Milvus Lite (local file)
        connections.connect(
            alias="default",
            uri=self.db_file  # Local file path for Milvus Lite
        )
        
        # Create collection if it doesn't exist
        if not utility.has_collection(self.collection_name):
            self._create_collection()
        else:
            self.collection = Collection(self.collection_name)
            self.collection.load()
    
    def _create_collection(self):
        """Create Milvus collection with schema."""
        # Define fields
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=255),
            FieldSchema(name="entity_type", dtype=DataType.VARCHAR, max_length=50),  # 'skill', 'job', 'candidate'
            FieldSchema(name="entity_id", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        ]
        
        # Create schema
        schema = CollectionSchema(
            fields=fields,
            description="Recruitment embeddings for skills, jobs, and candidates"
        )
        
        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # Create index for vector field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 256}
        }
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        self.collection.load()
        logger.info(f"Created collection {self.collection_name}")
    
    def store_skill_embedding(self, skill_name: str, embedding: np.ndarray):
        """Store a skill embedding."""
        data = [{
            "id": f"skill_{skill_name}",
            "entity_type": "skill",
            "entity_id": skill_name,
            "text": skill_name,
            "metadata": json.dumps({"skill_name": skill_name}),
            "embedding": embedding.tolist()
        }]
        
        # Check if exists and delete old version
        expr = f'id == "skill_{skill_name}"'
        self.collection.delete(expr)
        
        # Insert new
        self.collection.insert(data)
        self.collection.flush()
    
    def store_job_embeddings(self, job_id: str, embeddings: List[Dict]):
        """Store multiple job requirement embeddings."""
        data = []
        for idx, emb in enumerate(embeddings):
            data.append({
                "id": f"job_{job_id}_{idx}",
                "entity_type": "job",
                "entity_id": job_id,
                "text": emb['text'],
                "metadata": json.dumps({
                    "job_id": job_id,
                    "requirement_type": emb['type']
                }),
                "embedding": emb['embedding'].tolist()
            })
        
        # Delete old embeddings for this job
        expr = f'entity_id == "{job_id}" and entity_type == "job"'
        self.collection.delete(expr)
        
        # Insert new
        if data:
            self.collection.insert(data)
            self.collection.flush()
    
    def store_candidate_embeddings(self, candidate_id: str, embeddings: List[Dict]):
        """Store multiple candidate skill embeddings."""
        data = []
        for idx, emb in enumerate(embeddings):
            data.append({
                "id": f"candidate_{candidate_id}_{idx}",
                "entity_type": "candidate",
                "entity_id": candidate_id,
                "text": emb['skill'],
                "metadata": json.dumps({
                    "candidate_id": candidate_id,
                    "skill": emb['skill']
                }),
                "embedding": emb['embedding'].tolist()
            })
        
        # Delete old embeddings for this candidate
        expr = f'entity_id == "{candidate_id}" and entity_type == "candidate"'
        self.collection.delete(expr)
        
        # Insert new
        if data:
            self.collection.insert(data)
            self.collection.flush()
    
    def find_similar_skills(self, embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar skills using cosine similarity."""
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 64}
        }
        
        results = self.collection.search(
            data=[embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr='entity_type == "skill"',
            output_fields=["text"]
        )
        
        similar_skills = []
        for hits in results:
            for hit in hits:
                similar_skills.append((hit.entity.get('text'), hit.score))
        
        return similar_skills
    
    def match_candidate_to_job(self, job_id: str, candidate_id: str) -> Dict:
        """Match candidate skills against job requirements."""
        # Get job requirements
        job_expr = f'entity_id == "{job_id}" and entity_type == "job"'
        job_results = self.collection.query(
            expr=job_expr,
            output_fields=["text", "embedding", "metadata"]
        )
        
        # Get candidate skills
        cand_expr = f'entity_id == "{candidate_id}" and entity_type == "candidate"'
        cand_results = self.collection.query(
            expr=cand_expr,
            output_fields=["text", "embedding"]
        )
        
        requirement_matches = {}
        
        # For each job requirement, find best matching candidate skill
        for job_req in job_results:
            req_text = job_req['text']
            req_embedding = job_req['embedding']
            req_metadata = json.loads(job_req['metadata'])
            
            # Search for similar candidate skills
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 32}
            }
            
            results = self.collection.search(
                data=[req_embedding],
                anns_field="embedding",
                param=search_params,
                limit=5,
                expr=f'entity_id == "{candidate_id}" and entity_type == "candidate"',
                output_fields=["text"]
            )
            
            matches = []
            for hits in results:
                for hit in hits:
                    if hit.score > 0.75:  # Threshold for match
                        matches.append({
                            'skill': hit.entity.get('text'),
                            'similarity': hit.score
                        })
            
            if matches:
                requirement_matches[req_text] = {
                    'type': req_metadata.get('requirement_type', 'skill'),
                    'best_match': matches[0]['skill'],
                    'similarity': matches[0]['similarity'],
                    'all_matches': matches
                }
        
        return requirement_matches
    
    def cleanup_old_embeddings(self, entity_type: str, days: int = 30):
        """Clean up old embeddings (Note: Milvus Lite doesn't support time-based deletion easily)."""
        # For Milvus Lite, we would need to track timestamps separately
        # This is a simplified version that clears all of a specific type
        logger.warning(f"Cleanup not fully implemented for Milvus Lite. Would clear all {entity_type} embeddings.")
    
    def close(self):
        """Close Milvus connection."""
        if self.collection:
            self.collection.release()
        connections.disconnect("default")
```

#### Debugging Tips
- **Common Issue**: Milvus Lite file not found
  - **Solution**: Ensure parent directory exists before initializing
  - **Debug**: `os.makedirs(os.path.dirname(db_file), exist_ok=True)`
- **Common Issue**: Collection already exists error
  - **Solution**: Check existence before creating
  - **Debug**: `utility.has_collection(collection_name)`
- **Common Issue**: Similarity scores are unexpectedly low
  - **Solution**: Normalize embeddings before storing
  - **Debug**: `embedding = embedding / np.linalg.norm(embedding)`

### 3. Skill Ontology Service Component

#### Test Specification (tests/test_skill_ontology.py)

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from services.skill_ontology import SkillOntologyService

class TestSkillOntologyService:
    """Test skill normalization and semantic matching."""
    
    @pytest.fixture
    def skill_service(self):
        """Create skill service with mock OpenAI client."""
        with patch('services.skill_ontology.AsyncOpenAI') as mock_openai:
            service = SkillOntologyService(openai_api_key="test-key")
            service.client = mock_openai.return_value
            return service
    
    def test_normalize_common_abbreviations(self, skill_service):
        """Test: Should normalize common skill abbreviations."""
        # Test cases
        assert skill_service.normalize_skill("ML") == "machine_learning"
        assert skill_service.normalize_skill("JS") == "javascript"
        assert skill_service.normalize_skill("K8s") == "kubernetes"
        assert skill_service.normalize_skill("AI") == "artificial_intelligence"
    
    def test_case_insensitive_normalization(self, skill_service):
        """Test: Normalization should be case-insensitive."""
        assert skill_service.normalize_skill("python") == "python"
        assert skill_service.normalize_skill("Python") == "python"
        assert skill_service.normalize_skill("PYTHON") == "python"
    
    def test_preserve_unknown_skills(self, skill_service):
        """Test: Unknown skills should be preserved as-is."""
        unknown_skill = "quantum_computing"
        assert skill_service.normalize_skill(unknown_skill) == unknown_skill
    
    @pytest.mark.asyncio
    async def test_semantic_skill_matching(self, skill_service):
        """Test: Should find semantically similar skills."""
        # Arrange
        mock_vector_store = Mock()
        mock_vector_store.find_similar_skills.return_value = [
            ("machine_learning", 0.92),
            ("artificial_intelligence", 0.85),
            ("deep_learning", 0.83)
        ]
        skill_service.vector_store = mock_vector_store
        
        # Mock embedding response
        skill_service.client.embeddings.create = AsyncMock(
            return_value=Mock(data=[Mock(embedding=np.random.rand(1536).tolist())])
        )
        
        # Act
        result = await skill_service.find_similar_skill("ML Engineer", threshold=0.8)
        
        # Assert
        assert result == "machine_learning"
        mock_vector_store.find_similar_skills.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_embeddings(self, skill_service):
        """Test: Should initialize all skill embeddings in vector store."""
        # Arrange
        mock_vector_store = Mock()
        skill_service.vector_store = mock_vector_store
        
        # Mock embedding responses
        skill_service.client.embeddings.create = AsyncMock(
            return_value=Mock(data=[Mock(embedding=np.random.rand(1536).tolist())])
        )
        
        # Act
        await skill_service.initialize_embeddings(mock_vector_store)
        
        # Assert
        # Should store embeddings for all skills and their aliases
        assert mock_vector_store.store_skill_embedding.call_count > 20
        
        # Verify canonical skills were stored
        stored_skills = [
            call[0][0] for call in mock_vector_store.store_skill_embedding.call_args_list
        ]
        assert "machine_learning" in stored_skills
        assert "javascript" in stored_skills
        assert "ML" in stored_skills  # Aliases should also be stored

class TestSkillOntologyEdgeCases:
    """Test edge cases for skill ontology."""
    
    def test_empty_skill_normalization(self, skill_service):
        """Test: Empty or whitespace skills should be handled."""
        assert skill_service.normalize_skill("") == ""
        assert skill_service.normalize_skill("   ") == ""
    
    def test_skill_with_special_characters(self, skill_service):
        """Test: Skills with special characters should be normalized."""
        assert skill_service.normalize_skill("C++") == "C++"  # Preserve if not in ontology
        assert skill_service.normalize_skill("React.js") == "react"
        assert skill_service.normalize_skill("Node.JS") == "node.js"  # If in ontology
```

#### Minimal Implementation (services/skill_ontology.py)

```python
# src/services/skill_ontology.py
import json
from typing import Dict, List, Set, Optional
from pathlib import Path
import numpy as np
from openai import AsyncOpenAI
import asyncio
from services.vector_store import MilvusLiteStore

class SkillOntologyService:
    """Manages skill relationships and semantic understanding."""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.skill_graph = self._load_skill_graph()
        self.vector_store = None  # Will be set during initialization
    
    def _load_skill_graph(self) -> Dict[str, List[str]]:
        """Load skill aliases and relationships."""
        skill_data = {
            "machine_learning": ["ML", "machine learning", "deep learning", "DL", "neural networks"],
            "javascript": ["JS", "javascript", "ECMAScript", "ES6", "ES2015"],
            "react": ["React", "ReactJS", "React.js", "React Native"],
            "python": ["Python", "Python3", "Python 3.x"],
            "kubernetes": ["K8s", "Kubernetes", "k8s"],
            "amazon_web_services": ["AWS", "Amazon Web Services", "Amazon AWS"],
            "data_science": ["data science", "data analysis", "data analytics"],
            "software_engineering": ["SWE", "software development", "software engineer"],
            "artificial_intelligence": ["AI", "artificial intelligence", "A.I."],
            "natural_language_processing": ["NLP", "natural language processing", "text processing"],
            "computer_vision": ["CV", "computer vision", "image processing"],
            "devops": ["DevOps", "Dev Ops", "CI/CD", "continuous integration"],
            "docker": ["Docker", "containerization", "containers"],
            "sql": ["SQL", "Structured Query Language", "MySQL", "PostgreSQL", "database"],
            "nosql": ["NoSQL", "MongoDB", "Cassandra", "DynamoDB"],
            "api": ["API", "REST", "RESTful", "GraphQL", "web services"],
            "microservices": ["microservices", "micro-services", "service-oriented architecture"],
            "cloud": ["cloud computing", "cloud", "GCP", "Azure", "cloud platforms"],
            "agile": ["Agile", "Scrum", "Kanban", "agile methodology"],
            "git": ["Git", "GitHub", "GitLab", "version control", "source control"]
        }
        return skill_data
    
    async def initialize_embeddings(self, vector_store: MilvusLiteStore):
        """Initialize skill embeddings in pgvector."""
        self.vector_store = vector_store
        
        # Get all skills to embed
        all_skills = set()
        for canonical, aliases in self.skill_graph.items():
            all_skills.add(canonical)
            all_skills.update(aliases)
        
        # Store embeddings in pgvector using OpenAI
        for skill in all_skills:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=skill
            )
            embedding = np.array(response.data[0].embedding)
            self.vector_store.store_skill_embedding(skill, embedding)
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill to canonical form."""
        skill_lower = skill.lower().strip()
        
        # Direct match
        for canonical, aliases in self.skill_graph.items():
            if skill_lower == canonical or skill_lower in [a.lower() for a in aliases]:
                return canonical
        
        # Semantic match
        best_match = self.find_similar_skill(skill, threshold=0.85)
        return best_match if best_match else skill
    
    async def find_similar_skill(self, skill: str, threshold: float = 0.8) -> Optional[str]:
        """Find semantically similar skill using pgvector."""
        if not self.vector_store:
            return None
            
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=skill
        )
        skill_embedding = np.array(response.data[0].embedding)
        similar_skills = self.vector_store.find_similar_skills(skill_embedding, top_k=5)
        
        # Find the best match among canonical skills
        for similar_skill, similarity in similar_skills:
            if similarity > threshold:
                # Check if it's a canonical skill or find its canonical form
                for canonical, aliases in self.skill_graph.items():
                    if similar_skill == canonical or similar_skill in aliases:
                        return canonical
        
        return None
```

#### Debugging Tips
- **Common Issue**: Skills not normalizing correctly
  - **Solution**: Check skill_graph keys are lowercase
  - **Debug**: `print(self.skill_graph.keys())`
- **Common Issue**: Semantic matching returns no results
  - **Solution**: Ensure embeddings were initialized
  - **Debug**: Check vector store has skills: `vector_store.collection.num_entities`
- **Common Issue**: API rate limits on embedding generation
  - **Solution**: Add retry logic with exponential backoff
  - **Debug**: `await asyncio.sleep(1)` between embedding calls

### 4. Unified Recruitment Agent Component

#### Test Specification (tests/test_unified_agent.py)

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
from datetime import datetime
from sqlmodel import Session

from agents.unified_agent import UnifiedRecruitmentAgent, EvaluationResult
from models.database import Job, Candidate, Evaluation

class TestUnifiedRecruitmentAgent:
    """Test the main recruitment agent functionality."""
    
    @pytest.fixture
    def mock_config(self):
        return {
            "openai_api_key": "test-key",
            "database_url": "postgresql://test",
            "milvus_lite_file": "./test_milvus.db",
            "redis_host": "localhost",
            "redis_port": 6379,
            "hitl_confidence_threshold": 0.85,
            "embedding_dimension": 1536
        }
    
    @pytest.fixture
    def agent(self, mock_config):
        with patch('agents.unified_agent.OpenAI'), \
             patch('agents.unified_agent.OpenAIEmbedding'), \
             patch('agents.unified_agent.MilvusLiteStore'), \
             patch('agents.unified_agent.SkillOntologyService'):
            return UnifiedRecruitmentAgent(mock_config)
    
    @pytest.mark.asyncio
    async def test_job_requirement_decomposition(self, agent):
        """Test: Should correctly decompose job requirements."""
        # Arrange
        job_description = "Senior Python Developer, 5+ years, FastAPI experience"
        mock_response = Mock(text=json.dumps({
            "technical_skills": ["Python", "FastAPI"],
            "experience_years": {"minimum": 5, "preferred": 7},
            "education": {"level": "Bachelor's", "fields": ["Computer Science"]},
            "soft_skills": ["Communication"],
            "domain": ["Web Development"],
            "nice_to_have": ["Docker"]
        }))
        agent.llm.acomplete = AsyncMock(return_value=mock_response)
        
        # Act
        result = await agent._decompose_job_requirements(job_description, "workflow_123")
        
        # Assert
        assert result["technical_skills"] == ["python", "fastapi"]  # Normalized
        assert result["experience_years"]["minimum"] == 5
        assert "skill_embeddings" in result
    
    @pytest.mark.asyncio
    async def test_resume_parsing(self, agent):
        """Test: Should extract structured data from resume."""
        # Arrange
        resume_text = """John Doe
        Python Developer - 6 years
        Skills: Python, FastAPI, Docker
        Experience: Built APIs at TechCorp"""
        
        mock_response = Mock(text=json.dumps({
            "skills": {
                "technical": ["Python", "FastAPI", "Docker"],
                "soft": ["Problem Solving"]
            },
            "experience": [{
                "company": "TechCorp",
                "title": "Python Developer",
                "duration": "6 years",
                "achievements": ["Built APIs"]
            }],
            "education": [],
            "certifications": [],
            "projects": []
        }))
        agent.llm.acomplete = AsyncMock(return_value=mock_response)
        
        # Act
        result = await agent._parse_resume(resume_text, "workflow_123")
        
        # Assert
        assert "python" in result["skills"]["technical"]  # Normalized
        assert result["total_experience_years"] == 6.0
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, agent):
        """Test: Should calculate confidence correctly."""
        # Arrange
        screening_result = {"score": 0.8}
        critic_result = {
            "score": 0.75,
            "confidence_in_assessment": 0.9,
            "bias_flags": [],
            "hidden_gem": False,
            "transferable_skills": []
        }
        
        # Act
        confidence_metrics = agent._calculate_confidence(screening_result, critic_result)
        
        # Assert
        assert 0.8 < confidence_metrics["confidence"] < 0.9
        assert not confidence_metrics["needs_review"]
        assert confidence_metrics["score_difference"] == 0.05
    
    @pytest.mark.asyncio
    async def test_hidden_gem_detection(self, agent):
        """Test: Should identify hidden gem candidates."""
        # Arrange
        screening_result = {"score": 0.35}
        critic_result = {
            "score": 0.75,
            "confidence_in_assessment": 0.85,
            "bias_flags": ["non_traditional_education"],
            "hidden_gem": True,
            "transferable_skills": [
                {"from": "data_analysis", "to": "data_science"}
            ]
        }
        
        # Act
        confidence_metrics = agent._calculate_confidence(screening_result, critic_result)
        
        # Assert
        assert confidence_metrics["special_cases"]["hidden_gem"]
        assert confidence_metrics["needs_review"]
        assert confidence_metrics["review_type"] == "deep"
        assert confidence_metrics["review_priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_full_evaluation_workflow(self, agent, mock_session):
        """Test: Should complete full evaluation workflow."""
        # Arrange
        job_desc = "Python Developer"
        resume = "John Doe, Python expert"
        
        # Mock all sub-methods
        agent._init_workflow_state = AsyncMock()
        agent._decompose_job_requirements = AsyncMock(return_value={
            "technical_skills": ["python"],
            "experience_years": {"minimum": 3}
        })
        agent._parse_resume = AsyncMock(return_value={
            "skills": {"technical": ["python"]},
            "total_experience_years": 5
        })
        agent._semantic_screening = AsyncMock(return_value={
            "score": 0.85,
            "matched_skills": [{"required": "python", "found": "python", "confidence": 1.0}],
            "missing_skills": []
        })
        agent._critical_review = AsyncMock(return_value={
            "score": 0.88,
            "bias_flags": [],
            "transferable_skills": []
        })
        agent._log_evaluation = AsyncMock()
        agent._generate_explanation = AsyncMock(return_value="Strong match")
        
        # Act
        result = await agent.process_job_application(
            job_desc, resume, "job_123", "cand_456", mock_session
        )
        
        # Assert
        assert isinstance(result, EvaluationResult)
        assert result.screening_score == 0.85
        assert result.critic_score == 0.88
        assert not result.needs_review
        assert result.explanation == "Strong match"

class TestAgentEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_llm_failure_handling(self, agent):
        """Test: Should handle LLM failures gracefully."""
        # Arrange
        agent.llm.acomplete = AsyncMock(side_effect=Exception("API Error"))
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await agent._decompose_job_requirements("test job", "workflow_123")
        assert "API Error" in str(exc_info.value)
    
    def test_experience_parsing_edge_cases(self, agent):
        """Test: Should handle various experience formats."""
        assert agent._parse_duration("5 years") == 5.0
        assert agent._parse_duration("2 years 6 months") == 2.5
        assert agent._parse_duration("6 months") == 0.5
        assert agent._parse_duration("no experience") == 0.0
```

#### Minimal Implementation (agents/unified_agent.py)

```python
# src/agents/unified_agent.py
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from uuid import uuid4

from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
import redis.asyncio as redis
from sqlmodel import Session, select
import numpy as np
import asyncpg

from models.database import Job, Candidate, Evaluation, AuditLog
from services.skill_ontology import SkillOntologyService
from services.vector_store import MilvusLiteStore
from services.bias_detector import BiasDetectionService
from utils.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    screening_score: float
    critic_score: float
    confidence: float
    needs_review: bool
    explanation: str
    bias_flags: List[str]
    matched_skills: List[Dict[str, float]]
    missing_skills: List[str]
    transferable_skills: List[Dict[str, str]]

class UnifiedRecruitmentAgent:
    """
    Unified agent combining all sub-agent functionalities for POC.
    In production, these would be separate microservices.
    """
    
    def __init__(self, config: Dict):
        # Initialize services
        self.config = config
        self.skill_ontology = SkillOntologyService(config["openai_api_key"])
        self.bias_detector = BiasDetectionService()
        self.audit_logger = AuditLogger()
        
        # Initialize LLM components
        self.llm = OpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=config["openai_api_key"]
        )
        self.embedding_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=config["openai_api_key"]
        )
        
        # Initialize vector store with Milvus Lite
        self.vector_store = MilvusLiteStore(
            db_file=config.get("milvus_lite_file", "./milvus_lite.db"),
            collection_name=config.get("milvus_collection_name", "recruitment_embeddings"),
            embedding_dim=config.get("embedding_dimension", 1536)
        )
        
        # Initialize Redis for state management
        self.redis_client = None
        self.confidence_threshold = config.get("hitl_confidence_threshold", 0.85)
    
    async def initialize(self):
        """Initialize async connections."""
        # Initialize Milvus Lite store (synchronous)
        self.vector_store.initialize()
        
        # Initialize Redis
        self.redis_client = await redis.create_redis_pool(
            f"redis://{self.config['redis_host']}:{self.config['redis_port']}"
        )
        
        # Pre-populate skill embeddings if needed
        await self.skill_ontology.initialize_embeddings(self.vector_store)
    
    async def process_job_application(
        self,
        job_description: str,
        resume: str,
        job_id: str,
        candidate_id: str,
        session: Session
    ) -> EvaluationResult:
        """
        Main entry point orchestrating all agent functionalities.
        """
        workflow_id = f"{job_id}_{candidate_id}_{uuid4().hex[:8]}"
        
        try:
            # Initialize workflow state
            await self._init_workflow_state(workflow_id)
            
            # 1. SUPERVISOR: Decompose job requirements
            logger.info(f"[{workflow_id}] Decomposing job requirements")
            evaluation_rubric = await self._decompose_job_requirements(
                job_description, workflow_id
            )
            
            # 2. SOURCING: Parse and structure resume
            logger.info(f"[{workflow_id}] Parsing resume")
            parsed_resume = await self._parse_resume(resume, workflow_id)
            
            # 3. SCREENING: Semantic matching and scoring
            logger.info(f"[{workflow_id}] Performing semantic screening")
            screening_result = await self._semantic_screening(
                parsed_resume, evaluation_rubric, workflow_id
            )
            
            # 4. CRITIC: Bias check and second opinion
            logger.info(f"[{workflow_id}] Running critical review")
            critic_result = await self._critical_review(
                parsed_resume, evaluation_rubric, screening_result, workflow_id
            )
            
            # 5. HITL: Calculate confidence and routing
            logger.info(f"[{workflow_id}] Calculating confidence metrics")
            confidence_metrics = self._calculate_confidence(
                screening_result, critic_result
            )
            
            # 6. DATA-STEWARD: Log evaluation
            logger.info(f"[{workflow_id}] Logging evaluation")
            await self._log_evaluation(
                workflow_id, screening_result, critic_result,
                confidence_metrics, session
            )
            
            # Generate comprehensive explanation
            explanation = await self._generate_explanation(
                screening_result, critic_result, confidence_metrics
            )
            
            return EvaluationResult(
                screening_score=screening_result["score"],
                critic_score=critic_result["score"],
                confidence=confidence_metrics["confidence"],
                needs_review=confidence_metrics["needs_review"],
                explanation=explanation,
                bias_flags=critic_result.get("bias_flags", []),
                matched_skills=screening_result.get("matched_skills", []),
                missing_skills=screening_result.get("missing_skills", []),
                transferable_skills=critic_result.get("transferable_skills", [])
            )
            
        except Exception as e:
            logger.error(f"[{workflow_id}] Error: {str(e)}")
            await self._log_error(workflow_id, str(e), session)
            raise
    
    # ========== SUPERVISOR FUNCTIONALITY ==========
    
    async def _decompose_job_requirements(self, job_description: str, workflow_id: str) -> Dict:
        """
        Supervisor agent: Parse job description into evaluation criteria.
        """
        prompt = f"""
        Analyze this job description and extract structured requirements.
        
        Job Description: {job_description}
        
        Extract:
        1. Required technical skills (be specific, include frameworks/tools)
        2. Years of experience required (minimum and preferred)
        3. Education requirements (degree level and field)
        4. Soft skills (communication, leadership, etc.)
        5. Domain experience (industry knowledge)
        6. Nice-to-have skills (not required but beneficial)
        
        Return as JSON with these exact keys:
        {{
            "technical_skills": ["skill1", "skill2"],
            "experience_years": {{
                "minimum": 0,
                "preferred": 0
            }},
            "education": {{
                "level": "Bachelor's/Master's/PhD/Any",
                "fields": ["field1", "field2"]
            }},
            "soft_skills": ["skill1", "skill2"],
            "domain": ["domain1", "domain2"],
            "nice_to_have": ["skill1", "skill2"]
        }}
        """
        
        response = await self.llm.acomplete(prompt)
        rubric = json.loads(response.text)
        
        # Normalize skills using ontology
        rubric["technical_skills"] = [
            self.skill_ontology.normalize_skill(skill)
            for skill in rubric["technical_skills"]
        ]
        
        # Store job requirement embeddings in pgvector
        job_embeddings = []
        for skill in rubric["technical_skills"]:
            embedding = self.embedding_model.get_text_embedding(skill)
            job_embeddings.append({
                'type': 'skill',
                'text': skill,
                'embedding': np.array(embedding)
            })
        
        self.vector_store.store_job_embeddings(job_id, job_embeddings)
        rubric["skill_embeddings"] = {skill: emb['embedding'] for skill, emb in zip(rubric["technical_skills"], job_embeddings)}
        
        await self.audit_logger.log_async(
            workflow_id=workflow_id,
            agent="supervisor",
            action="decompose_requirements",
            data={"rubric": rubric}
        )
        
        return rubric
    
    # ========== SUPERVISOR FUNCTIONALITY ==========
    
    async def _decompose_job_requirements(self, job_description: str) -> Dict:
        """
        Supervisor agent functionality: Parse job description into evaluation criteria.
        """
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills
        2. Experience requirements
        3. Education requirements
        4. Soft skills
        5. Domain experience
        
        Job Description: {job_description}
        
        Return as structured JSON.
        """
        
        response = await self.llm.aquery(prompt)
        rubric = self._parse_llm_json(response)
        
        # Enrich with skill embeddings
        rubric["skill_embeddings"] = self._compute_skill_embeddings(
            rubric["technical_skills"]
        )
        
        return rubric
    
    # ========== SOURCING FUNCTIONALITY ==========
    
    async def _parse_resume(self, resume_text: str, workflow_id: str) -> Dict:
        """
        Sourcing agent: Extract structured data from resume.
        """
        prompt = f"""
        Extract structured information from this resume.
        
        Resume: {resume_text}
        
        Return as JSON with these exact keys:
        {{
            "skills": {{
                "technical": ["skill1", "skill2"],
                "soft": ["skill1", "skill2"]
            }},
            "experience": [
                {{
                    "company": "Company Name",
                    "title": "Job Title",
                    "duration": "X years Y months",
                    "achievements": ["achievement1", "achievement2"]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree Type",
                    "field": "Field of Study",
                    "institution": "University Name",
                    "year": "Graduation Year"
                }}
            ],
            "certifications": ["cert1", "cert2"],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Brief description",
                    "technologies": ["tech1", "tech2"]
                }}
            ]
        }}
        """
        
        response = await self.llm.acomplete(prompt)
        parsed_data = json.loads(response.text)
        
        # Normalize technical skills
        parsed_data["skills"]["technical"] = [
            self.skill_ontology.normalize_skill(skill)
            for skill in parsed_data["skills"]["technical"]
        ]
        
        # Store candidate skill embeddings in pgvector
        candidate_embeddings = []
        for skill in parsed_data["skills"]["technical"]:
            embedding = self.embedding_model.get_text_embedding(skill)
            candidate_embeddings.append({
                'skill': skill,
                'embedding': np.array(embedding)
            })
        
        self.vector_store.store_candidate_embeddings(candidate_id, candidate_embeddings)
        
        # Calculate total experience
        total_years = sum(
            self._parse_duration(exp["duration"])
            for exp in parsed_data["experience"]
        )
        parsed_data["total_experience_years"] = total_years
        
        await self.audit_logger.log_async(
            workflow_id=workflow_id,
            agent="sourcing",
            action="parse_resume",
            data={"parsed_skills_count": len(parsed_data["skills"]["technical"])}
        )
        
        return parsed_data
    
    def _parse_duration(self, duration: str) -> float:
        """Parse duration string to years."""
        import re
        years = re.findall(r'(\d+)\s*year', duration.lower())
        months = re.findall(r'(\d+)\s*month', duration.lower())
        
        total_years = 0
        if years:
            total_years += int(years[0])
        if months:
            total_years += int(months[0]) / 12
        
        return total_years
    
    # ========== SCREENING FUNCTIONALITY ==========
    
    async def _semantic_screening(
        self,
        parsed_resume: Dict,
        evaluation_rubric: Dict,
        workflow_id: str
    ) -> Dict:
        """
        Screening agent: Semantic matching and scoring.
        """
        # Extract candidate skills
        candidate_skills = parsed_resume["skills"]["technical"]
        required_skills = evaluation_rubric["technical_skills"]
        
        # Match skills using pgvector similarity search
        job_id = workflow_id.split("_")[0]
        candidate_id = workflow_id.split("_")[1]
        
        # Get matches from Milvus Lite
        skill_matches_raw = self.vector_store.match_candidate_to_job(job_id, candidate_id)
        
        # Process pgvector matches into structured format
        skill_matches = []
        missing_skills = list(required_skills)  # Start with all skills as missing
        
        for req_skill, match_data in skill_matches_raw.items():
            if match_data['similarity'] > 0.75:  # Good match found
                skill_matches.append({
                    "required": req_skill,
                    "found": match_data['best_match'],
                    "confidence": match_data['similarity']
                })
                # Remove from missing skills
                if req_skill in missing_skills:
                    missing_skills.remove(req_skill)
        
        # Calculate skill score
        skill_score = len(skill_matches) / len(required_skills) if required_skills else 0
        
        # Experience matching
        experience_score = self._evaluate_experience(
            parsed_resume.get("total_experience_years", 0),
            evaluation_rubric["experience_years"]
        )
        
        # Education matching
        education_score = self._evaluate_education(
            parsed_resume["education"],
            evaluation_rubric["education"]
        )
        
        # Domain matching
        domain_score = self._evaluate_domain(
            parsed_resume,
            evaluation_rubric.get("domain", [])
        )
        
        # Weighted scoring
        weights = {
            "skills": 0.40,
            "experience": 0.30,
            "education": 0.15,
            "domain": 0.15
        }
        
        final_score = (
            skill_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"] +
            domain_score * weights["domain"]
        )
        
        result = {
            "score": final_score,
            "components": {
                "skills": skill_score,
                "experience": experience_score,
                "education": education_score,
                "domain": domain_score
            },
            "matched_skills": skill_matches,
            "missing_skills": missing_skills,
            "details": {
                "total_required_skills": len(required_skills),
                "matched_skills_count": len(skill_matches),
                "candidate_experience_years": parsed_resume.get("total_experience_years", 0),
                "required_experience_years": evaluation_rubric["experience_years"]
            }
        }
        
        await self.audit_logger.log_async(
            workflow_id=workflow_id,
            agent="screening",
            action="semantic_match",
            data={
                "final_score": final_score,
                "matched_skills": len(skill_matches),
                "missing_skills": len(missing_skills)
            }
        )
        
        return result
    
    def _evaluate_experience(self, candidate_years: float, requirements: Dict) -> float:
        """Evaluate experience match."""
        min_years = requirements.get("minimum", 0)
        pref_years = requirements.get("preferred", min_years)
        
        if candidate_years >= pref_years:
            return 1.0
        elif candidate_years >= min_years:
            # Linear scale between min and preferred
            return 0.7 + 0.3 * (candidate_years - min_years) / (pref_years - min_years)
        elif candidate_years >= min_years - 1:
            # Close to minimum, partial credit
            return 0.5 + 0.2 * (candidate_years - (min_years - 1))
        else:
            # Below minimum
            return max(0, 0.3 * candidate_years / min_years)
    
    def _evaluate_education(self, candidate_education: List[Dict], requirements: Dict) -> float:
        """Evaluate education match."""
        req_level = requirements.get("level", "Any").lower()
        req_fields = [f.lower() for f in requirements.get("fields", [])]
        
        if req_level == "any":
            return 1.0
        
        level_hierarchy = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "bachelor's": 3,
            "master": 4,
            "master's": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        best_score = 0
        for edu in candidate_education:
            degree_level = edu.get("degree", "").lower()
            field = edu.get("field", "").lower()
            
            # Level match
            cand_level = level_hierarchy.get(degree_level.split()[0], 0)
            req_level_num = level_hierarchy.get(req_level.split()[0], 3)
            
            if cand_level >= req_level_num:
                level_score = 1.0
            else:
                level_score = 0.5 * (cand_level / req_level_num)
            
            # Field match
            field_score = 0
            if not req_fields or any(rf in field for rf in req_fields):
                field_score = 1.0
            elif any(word in field for word in ["computer", "software", "engineering", "science"]):
                field_score = 0.7  # Related field
            
            best_score = max(best_score, level_score * 0.6 + field_score * 0.4)
        
        return best_score
    
    def _evaluate_domain(self, parsed_resume: Dict, required_domains: List[str]) -> float:
        """Evaluate domain/industry experience."""
        if not required_domains:
            return 1.0
        
        # Check experience and projects for domain keywords
        resume_text = json.dumps(parsed_resume).lower()
        matched_domains = 0
        
        for domain in required_domains:
            if domain.lower() in resume_text:
                matched_domains += 1
        
        return matched_domains / len(required_domains)
    
    # ========== CRITIC FUNCTIONALITY ==========
    
    async def _critical_review(
        self,
        parsed_resume: Dict,
        evaluation_rubric: Dict,
        screening_result: Dict,
        workflow_id: str
    ) -> Dict:
        """
        Critic agent: Bias detection and second opinion.
        """
        bias_flags = []
        adjustments = []
        
        # 1. Check for non-traditional education
        education_analysis = self._analyze_education_bias(
            parsed_resume["education"],
            evaluation_rubric["education"]
        )
        if education_analysis["is_non_traditional"]:
            bias_flags.append("non_traditional_education")
            adjustments.append({
                "type": "education",
                "adjustment": 0.1,
                "reason": education_analysis["reason"]
            })
        
        # 2. Identify transferable skills
        transferable_skills = await self._identify_transferable_skills(
            parsed_resume,
            evaluation_rubric,
            screening_result["missing_skills"]
        )
        
        if transferable_skills:
            adjustments.append({
                "type": "transferable_skills",
                "adjustment": 0.15,
                "reason": f"Found {len(transferable_skills)} transferable skills"
            })
        
        # 3. Check for career gaps or transitions
        career_analysis = self._analyze_career_pattern(parsed_resume["experience"])
        if career_analysis["has_gaps"]:
            bias_flags.append("career_gaps")
        if career_analysis["is_career_changer"]:
            bias_flags.append("career_changer")
            adjustments.append({
                "type": "career_change",
                "adjustment": 0.1,
                "reason": "Career transition shows adaptability"
            })
        
        # 4. Check for diverse experience
        if self._has_diverse_experience(parsed_resume):
            adjustments.append({
                "type": "diverse_experience",
                "adjustment": 0.05,
                "reason": "Broad experience across domains"
            })
        
        # 5. Calculate adjusted score
        base_score = screening_result["score"]
        total_adjustment = sum(adj["adjustment"] for adj in adjustments)
        adjusted_score = min(base_score + total_adjustment, 1.0)
        
        # 6. Determine if this is a hidden gem
        is_hidden_gem = (
            base_score < 0.5 and adjusted_score > 0.7 or
            len(transferable_skills) >= 3 and base_score < 0.6
        )
        
        result = {
            "score": adjusted_score,
            "base_score": base_score,
            "adjustments": adjustments,
            "bias_flags": bias_flags,
            "transferable_skills": transferable_skills,
            "hidden_gem": is_hidden_gem,
            "confidence_in_assessment": self._calculate_critic_confidence(
                bias_flags, adjustments, transferable_skills
            )
        }
        
        await self.audit_logger.log_async(
            workflow_id=workflow_id,
            agent="critic",
            action="bias_review",
            data={
                "bias_flags": bias_flags,
                "score_adjustment": adjusted_score - base_score,
                "hidden_gem": is_hidden_gem
            }
        )
        
        return result
    
    def _analyze_education_bias(self, education: List[Dict], requirements: Dict) -> Dict:
        """Analyze for education-related biases."""
        traditional_institutions = [
            "university", "college", "institute of technology"
        ]
        
        for edu in education:
            institution = edu.get("institution", "").lower()
            degree = edu.get("degree", "").lower()
            
            # Check for bootcamps, online courses, self-taught
            if any(term in institution for term in ["bootcamp", "online", "coursera", "udacity"]):
                return {
                    "is_non_traditional": True,
                    "reason": "Bootcamp/online education background"
                }
            
            if "self" in degree or "self" in institution:
                return {
                    "is_non_traditional": True,
                    "reason": "Self-taught background"
                }
        
        return {"is_non_traditional": False, "reason": ""}
    
    async def _identify_transferable_skills(
        self,
        parsed_resume: Dict,
        evaluation_rubric: Dict,
        missing_skills: List[str]
    ) -> List[Dict[str, str]]:
        """Identify transferable skills that could compensate for missing direct skills."""
        transferable_map = {
            "data_analysis": ["data_science", "machine_learning", "business_intelligence"],
            "project_management": ["team_lead", "scrum_master", "product_owner"],
            "problem_solving": ["algorithm_design", "system_design", "debugging"],
            "programming": ["software_development", "coding", "scripting"],
            "database": ["sql", "data_modeling", "data_warehousing"],
            "web_development": ["frontend", "backend", "full_stack"],
            "mobile_development": ["ios", "android", "react_native"],
            "cloud": ["aws", "azure", "gcp", "devops"],
            "analytics": ["business_intelligence", "reporting", "metrics"]
        }
        
        candidate_skills = set(
            parsed_resume["skills"]["technical"] + 
            parsed_resume["skills"].get("soft", [])
        )
        
        transferable_skills = []
        for missing in missing_skills:
            for candidate_skill in candidate_skills:
                # Check if candidate has related transferable skill
                for base_skill, related in transferable_map.items():
                    if (candidate_skill in base_skill or base_skill in candidate_skill) and \
                       any(r in missing.lower() for r in related):
                        transferable_skills.append({
                            "from": candidate_skill,
                            "to": missing,
                            "confidence": 0.8
                        })
                        break
        
        return transferable_skills
    
    def _analyze_career_pattern(self, experience: List[Dict]) -> Dict:
        """Analyze career progression and gaps."""
        if not experience:
            return {"has_gaps": False, "is_career_changer": False}
        
        # Sort by most recent first (would need date parsing in production)
        titles = [exp.get("title", "").lower() for exp in experience]
        
        # Check for career change
        tech_keywords = ["developer", "engineer", "programmer", "analyst"]
        non_tech_count = sum(1 for title in titles if not any(kw in title for kw in tech_keywords))
        is_career_changer = non_tech_count > len(titles) // 2
        
        # Check for gaps (simplified - would need date analysis in production)
        total_duration = sum(
            self._parse_duration(exp.get("duration", "0 years"))
            for exp in experience
        )
        
        return {
            "has_gaps": total_duration < len(experience) * 1.5,  # Rough heuristic
            "is_career_changer": is_career_changer
        }
    
    def _has_diverse_experience(self, parsed_resume: Dict) -> bool:
        """Check if candidate has experience across multiple domains."""
        domains = set()
        
        # Check projects
        for project in parsed_resume.get("projects", []):
            if "web" in str(project).lower():
                domains.add("web")
            if "mobile" in str(project).lower():
                domains.add("mobile")
            if "data" in str(project).lower():
                domains.add("data")
            if "cloud" in str(project).lower():
                domains.add("cloud")
        
        return len(domains) >= 3
    
    def _calculate_critic_confidence(self, bias_flags: List[str], 
                                   adjustments: List[Dict],
                                   transferable_skills: List[Dict]) -> float:
        """Calculate critic's confidence in its assessment."""
        base_confidence = 0.8
        
        # More bias flags = less confidence
        base_confidence -= len(bias_flags) * 0.05
        
        # More adjustments = more nuanced analysis
        base_confidence += min(len(adjustments) * 0.03, 0.15)
        
        # Transferable skills increase confidence
        base_confidence += min(len(transferable_skills) * 0.02, 0.1)
        
        return max(0.5, min(1.0, base_confidence))
    
    # ========== HITL FUNCTIONALITY ==========
    
    def _calculate_confidence(
        self,
        screening_result: Dict,
        critic_result: Dict
    ) -> Dict:
        """
        HITL agent: Confidence scoring and routing logic.
        """
        screening_score = screening_result["score"]
        critic_score = critic_result["score"]
        
        # Calculate agreement between agents
        score_difference = abs(screening_score - critic_score)
        base_confidence = 1 - score_difference
        
        # Adjust confidence based on critic's confidence
        critic_confidence = critic_result.get("confidence_in_assessment", 0.8)
        adjusted_confidence = base_confidence * 0.7 + critic_confidence * 0.3
        
        # Special case detection
        hidden_gem = (
            critic_result.get("hidden_gem", False) or
            (critic_score >= 0.70 and screening_score <= 0.40)
        )
        
        false_positive = (
            screening_score >= 0.85 and 
            critic_score <= 0.50 and
            len(critic_result.get("transferable_skills", [])) < 2
        )
        
        high_bias_risk = len(critic_result.get("bias_flags", [])) >= 2
        
        significant_adjustment = (
            critic_score - screening_score > 0.2 and
            len(critic_result.get("adjustments", [])) >= 2
        )
        
        # Determine if human review is needed
        needs_review = (
            adjusted_confidence < self.confidence_threshold or
            hidden_gem or
            false_positive or
            high_bias_risk or
            significant_adjustment
        )
        
        # Determine review type and priority
        review_priority = "normal"
        review_type = "none"
        
        if needs_review:
            if hidden_gem:
                review_type = "deep"
                review_priority = "high"
            elif false_positive:
                review_type = "validation"
                review_priority = "medium"
            elif adjusted_confidence < 0.65:
                review_type = "deep"
                review_priority = "high"
            elif high_bias_risk:
                review_type = "bias_check"
                review_priority = "high"
            else:
                review_type = "quick"
                review_priority = "normal"
        
        return {
            "confidence": adjusted_confidence,
            "base_confidence": base_confidence,
            "score_difference": score_difference,
            "needs_review": needs_review,
            "review_type": review_type,
            "review_priority": review_priority,
            "special_cases": {
                "hidden_gem": hidden_gem,
                "false_positive": false_positive,
                "high_bias_risk": high_bias_risk,
                "significant_adjustment": significant_adjustment
            },
            "review_reasons": self._get_review_reasons(
                adjusted_confidence,
                hidden_gem,
                false_positive,
                high_bias_risk,
                significant_adjustment
            )
        }
    
    def _get_review_reasons(self, confidence: float, hidden_gem: bool,
                          false_positive: bool, high_bias: bool,
                          significant_adjustment: bool) -> List[str]:
        """Get human-readable reasons for review."""
        reasons = []
        
        if confidence < self.confidence_threshold:
            reasons.append(f"Low confidence score: {confidence:.2%}")
        if hidden_gem:
            reasons.append("Potential hidden gem candidate detected")
        if false_positive:
            reasons.append("Possible false positive - high screening score but low critic score")
        if high_bias:
            reasons.append("Multiple bias indicators detected")
        if significant_adjustment:
            reasons.append("Significant score adjustment by critic agent")
        
        return reasons
    
    # ========== DATA-STEWARD FUNCTIONALITY ==========
    
    async def _log_evaluation(
        self,
        workflow_id: str,
        screening_result: Dict,
        critic_result: Dict,
        confidence_metrics: Dict,
        session: Session
    ):
        """
        Data-Steward: Audit logging and compliance.
        """
        # Create evaluation record
        evaluation = Evaluation(
            job_id=workflow_id.split("_")[0],
            candidate_id=workflow_id.split("_")[1],
            screening_score=screening_result["score"],
            critic_score=critic_result["score"],
            confidence=confidence_metrics["confidence"],
            needs_review=confidence_metrics["needs_review"],
            bias_flags=critic_result.get("bias_flags", [])
        )
        session.add(evaluation)
        
        # Create detailed audit log
        audit_data = {
            "screening_components": screening_result["components"],
            "matched_skills": len(screening_result.get("matched_skills", [])),
            "missing_skills": len(screening_result.get("missing_skills", [])),
            "critic_adjustments": critic_result.get("adjustments", []),
            "transferable_skills": len(critic_result.get("transferable_skills", [])),
            "review_reasons": confidence_metrics.get("review_reasons", []),
            "special_cases": confidence_metrics.get("special_cases", {})
        }
        
        audit_log = AuditLog(
            workflow_id=workflow_id,
            agent_type="data_steward",
            action="evaluation_complete",
            data=audit_data
        )
        session.add(audit_log)
        
        # Update Redis metrics for monitoring
        await self._update_metrics(confidence_metrics)
        
        await session.commit()
    
    async def _update_metrics(self, confidence_metrics: Dict):
        """Update real-time metrics in Redis."""
        if not self.redis_client:
            return
        
        # Update counters
        await self.redis_client.hincrby("recruitment:metrics", "total_evaluations", 1)
        
        if confidence_metrics["needs_review"]:
            await self.redis_client.hincrby("recruitment:metrics", "reviews_needed", 1)
        
        # Update confidence distribution
        confidence_bucket = int(confidence_metrics["confidence"] * 10)
        await self.redis_client.hincrby(
            "recruitment:confidence_distribution",
            f"bucket_{confidence_bucket}",
            1
        )
        
        # Track special cases
        for case, value in confidence_metrics["special_cases"].items():
            if value:
                await self.redis_client.hincrby(
                    "recruitment:special_cases",
                    case,
                    1
                )
    
    # ========== HELPER METHODS ==========
    
    async def _init_workflow_state(self, workflow_id: str):
        """Initialize workflow tracking in Redis."""
        if self.redis_client:
            await self.redis_client.hset(
                f"workflow:{workflow_id}",
                mapping={
                    "status": "started",
                    "start_time": datetime.utcnow().isoformat(),
                    "current_stage": "initialization"
                }
            )
    
    async def _compute_skill_embeddings(self, skills: List[str]) -> Dict[str, np.ndarray]:
        """Compute embeddings for a list of skills."""
        embeddings = []
        for skill in skills:
            embedding = self.embedding_model.get_text_embedding(skill)
            embeddings.append(np.array(embedding))
        return {skill: emb for skill, emb in zip(skills, embeddings)}
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _generate_explanation(self, screening_result: Dict,
                                  critic_result: Dict,
                                  confidence_metrics: Dict) -> str:
        """Generate human-readable explanation of the evaluation."""
        explanation_parts = []
        
        # Overall assessment
        if confidence_metrics["confidence"] > 0.85:
            explanation_parts.append(
                "Strong alignment between initial screening and bias-aware review."
            )
        else:
            explanation_parts.append(
                f"Moderate confidence ({confidence_metrics['confidence']:.2%}) due to "
                f"differing assessments between screening and critic agents."
            )
        
        # Skills assessment
        matched = len(screening_result.get("matched_skills", []))
        missing = len(screening_result.get("missing_skills", []))
        explanation_parts.append(
            f"Candidate matches {matched} required skills with {missing} gaps identified."
        )
        
        # Transferable skills
        transferable = critic_result.get("transferable_skills", [])
        if transferable:
            explanation_parts.append(
                f"Found {len(transferable)} transferable skills that could compensate for gaps."
            )
        
        # Bias considerations
        bias_flags = critic_result.get("bias_flags", [])
        if bias_flags:
            explanation_parts.append(
                f"Detected potential bias indicators: {', '.join(bias_flags)}. "
                "Score adjusted to ensure fair evaluation."
            )
        
        # Special cases
        if confidence_metrics["special_cases"].get("hidden_gem"):
            explanation_parts.append(
                "🌟 Potential hidden gem: Strong candidate who might be overlooked by traditional screening."
            )
        
        return " ".join(explanation_parts)
    
    async def _log_error(self, workflow_id: str, error: str, session: Session):
        """Log errors to audit trail."""
        audit_log = AuditLog(
            workflow_id=workflow_id,
            agent_type="unified_agent",
            action="error",
            data={"error": error, "timestamp": datetime.utcnow().isoformat()}
        )
        session.add(audit_log)
        await session.commit()

#### Debugging Tips
- **Common Issue**: Workflow gets stuck in initialization
  - **Solution**: Check Redis connection is active
  - **Debug**: `await redis_client.ping()`
- **Common Issue**: Confidence always below threshold
  - **Solution**: Verify score normalization [0,1]
  - **Debug**: Log intermediate scores at each stage
- **Common Issue**: Missing skill embeddings
  - **Solution**: Ensure skill ontology initialized before use
  - **Debug**: `await skill_ontology.initialize_embeddings(vector_store)`

# Supporting utilities
class BiasDetectionService:
    """Service for detecting various forms of bias in evaluation."""
    
    def __init__(self):
        self.patterns = self._load_bias_patterns()
    
    def _load_bias_patterns(self) -> Dict:
        """Load known bias patterns."""
        return {
            "education": [
                "ivy league", "top tier", "prestigious",
                "bootcamp", "self-taught", "online course"
            ],
            "experience": [
                "FAANG", "Fortune 500", "startup",
                "freelance", "contract", "consulting"
            ],
            "location": [
                "silicon valley", "bay area", "remote",
                "offshore", "international"
            ]
        }
```

### 5. Chainlit UI Integration Component

#### Test Specification (tests/test_chainlit_interface.py)

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
import chainlit as cl
from ui.chainlit_app import ChainlitRecruitmentInterface
from agents.unified_agent import EvaluationResult

class TestChainlitInterface:
    """Test Chainlit UI interactions."""
    
    @pytest.fixture
    def interface(self):
        with patch('ui.chainlit_app.UnifiedRecruitmentAgent'):
            return ChainlitRecruitmentInterface()
    
    @pytest.mark.asyncio
    async def test_start_message(self, interface):
        """Test: Should display welcome message on start."""
        # Arrange
        with patch('chainlit.Message') as mock_message:
            mock_msg_instance = Mock()
            mock_message.return_value = mock_msg_instance
            mock_msg_instance.send = AsyncMock()
            
            # Act
            await interface.start()
            
            # Assert
            mock_message.assert_called_once()
            args = mock_message.call_args[1]
            assert "Welcome" in args["content"]
            assert "AI Recruitment Assistant" in args["content"]
    
    @pytest.mark.asyncio
    async def test_demo_command(self, interface):
        """Test: Should run demo evaluation when 'demo' is typed."""
        # Arrange
        mock_message = Mock(content="demo", elements=[])
        interface.evaluate_candidate = AsyncMock()
        
        # Act
        await interface.main(mock_message)
        
        # Assert
        interface.evaluate_candidate.assert_called_once()
        # Should be called with demo job and resume
        call_args = interface.evaluate_candidate.call_args[0]
        assert "Python Developer" in call_args[0]
        assert "Jane Smith" in call_args[1]
    
    @pytest.mark.asyncio
    async def test_file_upload_processing(self, interface):
        """Test: Should process job description and resume uploads."""
        # Arrange
        job_file = Mock(name="job_description.txt", content="Python Developer needed")
        resume_file = Mock(name="resume.pdf", content="John Doe CV")
        mock_message = Mock(content="", elements=[job_file, resume_file])
        interface.evaluate_candidate = AsyncMock()
        
        # Act
        await interface.main(mock_message)
        
        # Assert
        interface.evaluate_candidate.assert_called_once_with(
            "Python Developer needed",
            "John Doe CV"
        )
    
    @pytest.mark.asyncio
    async def test_evaluation_results_display(self, interface):
        """Test: Should format evaluation results correctly."""
        # Arrange
        result = EvaluationResult(
            screening_score=0.85,
            critic_score=0.82,
            confidence=0.96,
            needs_review=False,
            explanation="Strong match for position",
            bias_flags=[],
            matched_skills=[{"required": "Python", "found": "Python", "confidence": 1.0}],
            missing_skills=["Docker"],
            transferable_skills=[]
        )
        
        # Act
        formatted = interface._format_evaluation_results(result)
        
        # Assert
        assert "85%" in formatted  # Screening score
        assert "82%" in formatted  # Critic score
        assert "96%" in formatted  # Confidence
        assert "Automated Approval" in formatted
        assert "Strong match" in formatted
    
    @pytest.mark.asyncio
    async def test_human_review_flow(self, interface):
        """Test: Should initiate review flow for low confidence."""
        # Arrange
        result = EvaluationResult(
            screening_score=0.45,
            critic_score=0.78,
            confidence=0.65,
            needs_review=True,
            explanation="Significant disagreement between agents",
            bias_flags=["non_traditional_education"],
            matched_skills=[],
            missing_skills=["Python", "FastAPI"],
            transferable_skills=[{"from": "Java", "to": "Python"}]
        )
        
        with patch('chainlit.Message') as mock_message, \
             patch('chainlit.user_session') as mock_session:
            mock_msg_instance = Mock()
            mock_message.return_value = mock_msg_instance
            mock_msg_instance.send = AsyncMock()
            
            # Act
            await interface.initiate_review_flow(result, "job desc", "resume")
            
            # Assert
            mock_session.set.assert_called()
            # Should set review mode
            calls = mock_session.set.call_args_list
            assert any(call[0][0] == "mode" and call[0][1] == "review" for call in calls)
            # Should show review message
            assert "Human Review Required" in mock_message.call_args[1]["content"]

class TestChainlitActions:
    """Test Chainlit action callbacks."""
    
    @pytest.mark.asyncio
    async def test_approve_action(self, interface):
        """Test: Approve action should log decision."""
        # Arrange
        with patch('chainlit.user_session') as mock_session, \
             patch('chainlit.Message') as mock_message:
            mock_session.get.return_value = {
                "result": Mock(screening_score=0.8)
            }
            interface.agent = Mock()
            interface.agent._log_human_decision = Mock()
            
            action = Mock()
            mock_msg_instance = Mock()
            mock_message.return_value = mock_msg_instance
            mock_msg_instance.send = AsyncMock()
            
            # Act
            await interface.on_approve(action)
            
            # Assert
            interface.agent._log_human_decision.assert_called_once_with(
                "approve", 
                {"result": mock_session.get.return_value["result"]}
            )
            assert "approved" in mock_message.call_args[1]["content"]
```

#### Minimal Implementation (ui/chainlit_app.py)

```python
import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider

class ChainlitRecruitmentInterface:
    """Chainlit-based chat interface for the recruitment system."""
    
    def __init__(self):
        self.agent = UnifiedRecruitmentAgent(config)
        self.active_reviews = {}
    
    @cl.on_chat_start
    async def start(self):
        """Initialize the chat session."""
        await cl.Message(
            content="""👋 Welcome to the AI Recruitment Assistant!
            
I can help you:
1. 📄 Evaluate resumes against job descriptions
2. 🎯 Identify qualified candidates with reduced bias
3. 🔍 Review candidates that need human attention
4. 📊 Provide detailed scoring explanations

Please upload a job description and resume to start, or type 'demo' to see a sample evaluation."""
        ).send()
        
        # Store agent in session
        cl.user_session.set("agent", self.agent)
        cl.user_session.set("mode", "evaluation")
    
    @cl.on_message
    async def main(self, message: cl.Message):
        """Handle incoming messages."""
        agent = cl.user_session.get("agent")
        mode = cl.user_session.get("mode")
        
        # Handle demo request
        if message.content.lower() == "demo":
            await self.run_demo_evaluation()
            return
        
        # Handle file uploads
        if message.elements:
            await self.process_file_uploads(message.elements)
            return
        
        # Handle review mode
        if mode == "review":
            await self.handle_review_decision(message.content)
            return
        
        # Default response
        await cl.Message(
            content="Please upload a job description and resume, or type 'demo' to see a sample evaluation."
        ).send()
    
    async def process_file_uploads(self, elements):
        """Process uploaded job description and resume."""
        job_desc = None
        resume = None
        
        for element in elements:
            if "job" in element.name.lower():
                job_desc = element.content
            elif "resume" in element.name.lower() or "cv" in element.name.lower():
                resume = element.content
        
        if job_desc and resume:
            await self.evaluate_candidate(job_desc, resume)
        else:
            await cl.Message(
                content="Please upload both a job description and a resume."
            ).send()
    
    async def evaluate_candidate(self, job_desc: str, resume: str):
        """Run the evaluation and present results."""
        # Show processing message
        msg = cl.Message(content="🔄 Analyzing resume against job requirements...")
        await msg.send()
        
        # Run evaluation
        agent = cl.user_session.get("agent")
        result = await agent.process_job_application(
            job_description=job_desc,
            resume=resume,
            job_id="JOB_DEMO",
            candidate_id="CAND_DEMO"
        )
        
        # Update message with results
        await msg.update(content=self._format_evaluation_results(result))
        
        # If review needed, start review flow
        if result.needs_review:
            await self.initiate_review_flow(result, job_desc, resume)
    
    def _format_evaluation_results(self, result: EvaluationResult) -> str:
        """Format evaluation results for display."""
        confidence_emoji = "🟢" if result.confidence > 0.85 else "🟡" if result.confidence > 0.65 else "🔴"
        
        return f"""## 📊 Evaluation Results

**Overall Assessment:**
- Screening Score: {result.screening_score:.2%}
- Critic Score: {result.critic_score:.2%}
- Confidence: {confidence_emoji} {result.confidence:.2%}

**Decision:** {"✅ Automated Approval" if not result.needs_review else "👤 Human Review Required"}

**Key Findings:**
{result.explanation}

**Bias Detection:**
{self._format_bias_flags(result.bias_flags)}

**Recommendation:** {self._get_recommendation(result)}
"""
    
    async def initiate_review_flow(self, result: EvaluationResult, job_desc: str, resume: str):
        """Start human-in-the-loop review process."""
        cl.user_session.set("mode", "review")
        cl.user_session.set("current_review", {
            "result": result,
            "job_desc": job_desc,
            "resume": resume
        })
        
        # Create action buttons
        actions = [
            cl.Action(
                name="approve",
                value="approve",
                label="✅ Approve Candidate",
                description="Move candidate to next round"
            ),
            cl.Action(
                name="reject",
                value="reject", 
                label="❌ Reject Candidate",
                description="Candidate doesn't meet requirements"
            ),
            cl.Action(
                name="request_info",
                value="request_info",
                label="📝 Request More Info",
                description="Need additional information"
            )
        ]
        
        await cl.Message(
            content=f"""## 👤 Human Review Required

**Why this needs review:**
{self._explain_review_reason(result)}

**Agent Disagreement Analysis:**
- Screening Agent: {result.screening_score:.2%} (traditional criteria)
- Critic Agent: {result.critic_score:.2%} (potential & bias check)
- Disagreement: {abs(result.screening_score - result.critic_score):.2%}

Please review the full analysis above and make a decision:""",
            actions=actions
        ).send()
    
    @cl.action_callback("approve")
    async def on_approve(self, action):
        """Handle approval action."""
        review_data = cl.user_session.get("current_review")
        
        # Log decision
        agent = cl.user_session.get("agent")
        agent._log_human_decision("approve", review_data["result"])
        
        await cl.Message(
            content="✅ Candidate approved! The decision has been logged for audit and learning purposes."
        ).send()
        
        cl.user_session.set("mode", "evaluation")
    
    @cl.action_callback("reject")
    async def on_reject(self, action):
        """Handle rejection action."""
        # Ask for rejection reason
        res = await cl.AskUserMessage(
            content="Please provide a brief reason for rejection:",
            timeout=60
        ).send()
        
        if res:
            review_data = cl.user_session.get("current_review")
            agent = cl.user_session.get("agent")
            agent._log_human_decision("reject", review_data["result"], reason=res["output"])
            
            await cl.Message(
                content="❌ Candidate rejected. The decision and reasoning have been logged."
            ).send()
        
        cl.user_session.set("mode", "evaluation")
    
    async def run_demo_evaluation(self):
        """Run a demonstration with sample data."""
        demo_job = """
        Senior Python Developer
        
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
        
        demo_resume = """
        Jane Smith
        Email: jane.smith@email.com | GitHub: github.com/janesmith
        
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
        
        await cl.Message(
            content="🎭 Running demo evaluation with sample Senior Python Developer position..."
        ).send()
        
        await self.evaluate_candidate(demo_job, demo_resume)
```

#### Debugging Tips
- **Common Issue**: Chainlit actions not triggering
  - **Solution**: Ensure action names match callback names exactly
  - **Debug**: Add logging in action callbacks
- **Common Issue**: File uploads not processing
  - **Solution**: Check element.content is accessible
  - **Debug**: `print(f"File: {element.name}, Size: {len(element.content)}")`
- **Common Issue**: Session data lost between messages
  - **Solution**: Always use cl.user_session for persistence
  - **Debug**: `print(cl.user_session.get("mode"))`

## 6. Integration Components (TDD Approach)

### API Endpoints Component

#### Test Specification (tests/test_api.py)

```python
import pytest
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock, patch
from api.main import app, EvaluationRequest
from agents.unified_agent import EvaluationResult

class TestAPIEndpoints:
    """Test FastAPI endpoints."""
    
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_evaluate_endpoint_success(self, client):
        """Test: Evaluation endpoint should return correct response."""
        # Arrange
        mock_result = EvaluationResult(
            screening_score=0.85,
            critic_score=0.80,
            confidence=0.95,
            needs_review=False,
            explanation="Good match",
            bias_flags=[],
            matched_skills=[],
            missing_skills=[]
        )
        
        with patch('api.main.agent') as mock_agent:
            mock_agent.process_job_application = AsyncMock(return_value=mock_result)
            
            # Act
            response = await client.post(
                "/evaluate",
                json={
                    "job_description": "Python Developer",
                    "resume": "John Doe resume",
                    "job_id": "job_123",
                    "candidate_id": "cand_456"
                }
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["screening_score"] == 0.85
            assert data["critic_score"] == 0.80
            assert data["confidence"] == 0.95
            assert not data["needs_review"]
    
    @pytest.mark.asyncio
    async def test_evaluate_endpoint_validation(self, client):
        """Test: Should validate required fields."""
        # Act - Missing required fields
        response = await client.post(
            "/evaluate",
            json={"job_description": "Python Developer"}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """Test: Metrics endpoint should return system metrics."""
        # Arrange
        with patch('api.main.agent.redis_client') as mock_redis:
            mock_redis.hgetall = AsyncMock(return_value={
                b"total_evaluations": b"100",
                b"reviews_needed": b"15"
            })
            
            # Act
            response = await client.get("/metrics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_evaluations"] == 100
            assert data["reviews_needed"] == 15
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test: Health check endpoint should return status."""
        # Act
        response = await client.get("/health")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

#### Minimal Implementation (api/main.py)

```python
# src/api/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel
import asyncio

from agents.unified_agent import UnifiedRecruitmentAgent
from models.database import get_session
from config import get_config

app = FastAPI(title="Recruitment POC API")

# Initialize agent
config = get_config()
agent = UnifiedRecruitmentAgent(config)

@app.on_event("startup")
async def startup():
    await agent.initialize()

class EvaluationRequest(BaseModel):
    job_description: str
    resume: str
    job_id: str
    candidate_id: str

@app.post("/evaluate")
async def evaluate_candidate(
    request: EvaluationRequest,
    session: Session = Depends(get_session)
):
    """Evaluate a candidate against a job description."""
    try:
        result = await agent.process_job_application(
            job_description=request.job_description,
            resume=request.resume,
            job_id=request.job_id,
            candidate_id=request.candidate_id,
            session=session
        )
        
        return {
            "screening_score": result.screening_score,
            "critic_score": result.critic_score,
            "confidence": result.confidence,
            "needs_review": result.needs_review,
            "explanation": result.explanation,
            "bias_flags": result.bias_flags,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    metrics = await agent.redis_client.hgetall("recruitment:metrics")
    return {k.decode(): int(v) for k, v in metrics.items()}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
```

#### Debugging Tips
- **Common Issue**: Agent not initialized on startup
  - **Solution**: Ensure startup event runs before requests
  - **Debug**: Add logging in startup event
- **Common Issue**: Database session errors
  - **Solution**: Use Depends(get_session) correctly
  - **Debug**: Check session is closed after each request
- **Common Issue**: Timeout on evaluation endpoint
  - **Solution**: Add async timeout handling
  - **Debug**: `asyncio.wait_for(agent.process_job_application(...), timeout=30)`

### Redis State Management Component

#### Test Specification (tests/test_redis_state.py)

```python
import pytest
from unittest.mock import Mock, AsyncMock
import json
from datetime import datetime
from services.redis_cache import RedisStateManager

class TestRedisStateManager:
    """Test Redis state management functionality."""
    
    @pytest.fixture
    def mock_redis(self):
        return Mock(spec=redis.Redis)
    
    @pytest.fixture
    def state_manager(self, mock_redis):
        return RedisStateManager(mock_redis)
    
    @pytest.mark.asyncio
    async def test_queue_for_review(self, state_manager, mock_redis):
        """Test: Should queue candidates for human review."""
        # Arrange
        workflow_id = "workflow_123"
        data = {
            "confidence": 0.65,
            "special_cases": {"hidden_gem": True}
        }
        mock_redis.zadd = AsyncMock()
        mock_redis.publish = AsyncMock()
        
        # Act
        await state_manager.queue_for_review(workflow_id, data)
        
        # Assert
        # Should add to sorted set with priority
        mock_redis.zadd.assert_called_once()
        call_args = mock_redis.zadd.call_args
        assert "hitl:queue" in call_args[0]
        
        # Should publish notification
        mock_redis.publish.assert_called_once_with(
            "hitl_queue",
            json.dumps({"type": "new_review", "workflow_id": workflow_id})
        )
    
    @pytest.mark.asyncio
    async def test_priority_calculation(self, state_manager):
        """Test: Should calculate correct priority for reviews."""
        # Test hidden gem - highest priority
        data1 = {"special_cases": {"hidden_gem": True}, "confidence": 0.8}
        priority1 = state_manager._calculate_priority(data1)
        
        # Test high bias risk
        data2 = {"special_cases": {"high_bias_risk": True}, "confidence": 0.8}
        priority2 = state_manager._calculate_priority(data2)
        
        # Test low confidence
        data3 = {"special_cases": {}, "confidence": 0.4}
        priority3 = state_manager._calculate_priority(data3)
        
        # Assert priorities
        assert priority1 > priority2  # Hidden gem > bias risk
        assert priority2 > priority3  # Bias risk > low confidence
        assert priority1 == 150  # Base 100 + 50 for hidden gem
    
    @pytest.mark.asyncio
    async def test_get_pending_reviews(self, state_manager, mock_redis):
        """Test: Should retrieve pending reviews sorted by priority."""
        # Arrange
        mock_reviews = [
            b'{"workflow_id": "w1", "status": "pending"}',
            b'{"workflow_id": "w2", "status": "pending"}'
        ]
        mock_redis.zrevrange = AsyncMock(return_value=mock_reviews)
        
        # Act
        reviews = await state_manager.get_pending_reviews(limit=10)
        
        # Assert
        assert len(reviews) == 2
        assert reviews[0]["workflow_id"] == "w1"
        mock_redis.zrevrange.assert_called_once_with("hitl:queue", 0, 9)
    
    @pytest.mark.asyncio
    async def test_update_workflow_state(self, state_manager, mock_redis):
        """Test: Should update workflow state tracking."""
        # Arrange
        workflow_id = "workflow_123"
        mock_redis.hset = AsyncMock()
        
        # Act
        await state_manager.update_workflow_state(
            workflow_id, 
            "screening", 
            {"score": 0.85}
        )
        
        # Assert
        mock_redis.hset.assert_called_once()
        call_args = mock_redis.hset.call_args
        assert f"workflow:{workflow_id}" in call_args[0]
```

#### Minimal Implementation (services/redis_cache.py)

```python
# src/services/redis_cache.py
import json
from typing import Optional, Dict, List
import redis.asyncio as redis
from datetime import datetime

class RedisStateManager:
    """Manages workflow state and HITL queue in Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hitl_channel = "hitl_queue"
    
    async def queue_for_review(self, workflow_id: str, data: Dict):
        """Queue a candidate for human review."""
        review_data = {
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "status": "pending"
        }
        
        # Add to sorted set by priority
        priority = self._calculate_priority(data)
        await self.redis.zadd(
            "hitl:queue",
            {json.dumps(review_data): priority}
        )
        
        # Publish notification
        await self.redis.publish(
            self.hitl_channel,
            json.dumps({"type": "new_review", "workflow_id": workflow_id})
        )
    
    async def get_pending_reviews(self, limit: int = 10) -> List[Dict]:
        """Get pending reviews sorted by priority."""
        items = await self.redis.zrevrange("hitl:queue", 0, limit - 1)
        return [json.loads(item) for item in items]
    
    def _calculate_priority(self, data: Dict) -> float:
        """Calculate review priority (higher = more urgent)."""
        base_priority = 100
        
        # Hidden gems get highest priority
        if data.get("special_cases", {}).get("hidden_gem"):
            base_priority += 50
        
        # High bias risk increases priority
        if data.get("special_cases", {}).get("high_bias_risk"):
            base_priority += 30
        
        # Low confidence increases priority
        confidence = data.get("confidence", 1.0)
        base_priority += (1 - confidence) * 20
        
        return base_priority
    
    async def update_workflow_state(self, workflow_id: str, stage: str, data: Dict):
        """Update workflow state tracking."""
        state_data = {
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "data": json.dumps(data)
        }
        
        await self.redis.hset(
            f"workflow:{workflow_id}",
            mapping=state_data
        )
```

#### Debugging Tips
- **Common Issue**: Redis connection refused
  - **Solution**: Ensure Redis is running on correct port
  - **Debug**: `docker-compose ps` or `redis-cli ping`
- **Common Issue**: Priority queue not ordering correctly
  - **Solution**: Use ZREVRANGE for descending order
  - **Debug**: `redis-cli zrange hitl:queue 0 -1 WITHSCORES`
- **Common Issue**: JSON serialization errors
  - **Solution**: Convert datetime objects to ISO format
  - **Debug**: Use `json.dumps(data, default=str)`

## 7. Comprehensive Testing Strategy

### Test Organization

```bash
tests/
├── unit/                  # Unit tests for individual components
│   ├── test_models.py
│   ├── test_vector_store.py
│   ├── test_skill_ontology.py
│   └── test_agent_methods.py
├── integration/          # Integration tests
│   ├── test_api_integration.py
│   ├── test_database_integration.py
│   └── test_redis_integration.py
├── e2e/                  # End-to-end tests
│   ├── test_full_workflow.py
│   └── test_ui_flows.py
├── performance/          # Performance tests
│   ├── test_load.py
│   └── test_embedding_speed.py
├── fixtures/            # Shared test data
│   ├── sample_jobs.json
│   ├── sample_resumes.json
│   └── expected_results.json
├── conftest.py          # Global fixtures
└── test_utils.py        # Test utilities
```

### Testing Pyramid Approach

```python
# tests/conftest.py - Global Test Configuration
import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from sqlmodel import create_engine, Session, SQLModel
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
import redis.asyncio as redis

# Set test environment
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"

@pytest.fixture(scope="session")
def postgres_container():
    """Spin up PostgreSQL container for tests."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    """Spin up Redis container for tests."""
    with RedisContainer("redis:7-alpine") as redis_cont:
        yield redis_cont

@pytest.fixture
async def db_session(postgres_container) -> AsyncGenerator[Session, None]:
    """Create test database session."""
    engine = create_engine(postgres_container.get_connection_url())
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
        session.rollback()

@pytest.fixture
async def redis_client(redis_container) -> AsyncGenerator[redis.Redis, None]:
    """Create test Redis client."""
    client = await redis.from_url(
        f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}"
    )
    yield client
    await client.flushall()
    await client.close()

# Mock factories
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
                "education": {"level": "Bachelor's", "fields": ["Computer Science"]}
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
            Education: BS Computer Science"""
        }
        defaults.update(kwargs)
        return defaults
    return _factory
```

### Test Categories

#### 1. Unit Tests (tests/unit/)

```python
# tests/unit/test_agent_methods.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

class TestAgentMethods:
    """Test individual agent methods in isolation."""
    
    @pytest.mark.asyncio
    async def test_decompose_job_requirements_parsing(self, agent):
        """Test: Job requirement decomposition should parse correctly."""
        # Arrange
        job_desc = "Python Developer, 5+ years, ML experience preferred"
        mock_llm_response = {
            "technical_skills": ["Python", "Machine Learning"],
            "experience_years": {"minimum": 5, "preferred": 7}
        }
        agent.llm.acomplete = AsyncMock(
            return_value=Mock(text=json.dumps(mock_llm_response))
        )
        
        # Act
        result = await agent._decompose_job_requirements(job_desc, "wf_123")
        
        # Assert
        assert "python" in result["technical_skills"]  # Normalized
        assert "machine_learning" in result["technical_skills"]
        assert result["experience_years"]["minimum"] == 5
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_edge_cases(self, agent):
        """Test: Confidence calculation handles edge cases."""
        test_cases = [
            # (screening_score, critic_score, expected_needs_review)
            (0.95, 0.93, False),  # High agreement, high scores
            (0.30, 0.85, True),   # Hidden gem
            (0.85, 0.30, True),   # False positive
            (0.50, 0.50, True),   # Low scores, perfect agreement
        ]
        
        for screen, critic, expected_review in test_cases:
            result = agent._calculate_confidence(
                {"score": screen},
                {"score": critic, "confidence_in_assessment": 0.8}
            )
            assert result["needs_review"] == expected_review
```

#### 2. Integration Tests (tests/integration/)

```python
# tests/integration/test_database_integration.py
import pytest
from sqlmodel import select
from models.database import Job, Candidate, Evaluation

class TestDatabaseIntegration:
    """Test database operations with real database."""
    
    @pytest.mark.asyncio
    async def test_full_evaluation_persistence(self, db_session, agent):
        """Test: Complete evaluation should persist correctly."""
        # Arrange
        job = Job(
            title="Python Developer",
            description="Need Python expert",
            requirements={"skills": ["Python"]}
        )
        candidate = Candidate(
            name="Jane Doe",
            email="jane@example.com",
            resume_text="Python developer with 5 years experience"
        )
        db_session.add_all([job, candidate])
        db_session.commit()
        
        # Act
        result = await agent.process_job_application(
            job.description,
            candidate.resume_text,
            str(job.id),
            str(candidate.id),
            db_session
        )
        
        # Assert
        evaluation = db_session.exec(
            select(Evaluation).where(
                Evaluation.job_id == job.id,
                Evaluation.candidate_id == candidate.id
            )
        ).first()
        
        assert evaluation is not None
        assert evaluation.screening_score == result.screening_score
        assert evaluation.confidence == result.confidence
```

#### 3. End-to-End Tests (tests/e2e/)

```python
# tests/e2e/test_full_workflow.py
import pytest
from httpx import AsyncClient

class TestFullWorkflow:
    """Test complete user workflows."""
    
    @pytest.mark.asyncio
    async def test_hidden_gem_workflow(self, client: AsyncClient):
        """Test: Hidden gem candidate flows through system correctly."""
        # Arrange - Self-taught developer
        job_desc = """Senior Python Developer
        Requirements:
        - BS Computer Science required
        - 5+ years Python experience
        - FastAPI, Docker experience"""
        
        resume = """Alex Chen - Full Stack Developer
        Self-taught programmer, bootcamp graduate
        4 years professional experience
        
        Skills: Python, JavaScript, Docker, AWS
        Projects: Built e-commerce platform handling 1M users
        Experience: Lead developer at startup (3 years)"""
        
        # Act - Submit evaluation
        response = await client.post("/evaluate", json={
            "job_description": job_desc,
            "resume": resume,
            "job_id": "job_001",
            "candidate_id": "cand_001"
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Should identify as needing review despite good skills
        assert data["needs_review"] == True
        assert "non_traditional_education" in data["bias_flags"]
        assert data["critic_score"] > data["screening_score"]
        assert "hidden gem" in data["explanation"].lower()
```

#### 4. Performance Tests (tests/performance/)

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from statistics import mean, stdev

class TestPerformance:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_evaluations(self, agent, mock_job_factory, mock_resume_factory):
        """Test: System should handle concurrent evaluations efficiently."""
        # Arrange
        num_concurrent = 10
        jobs = [mock_job_factory() for _ in range(num_concurrent)]
        resumes = [mock_resume_factory() for _ in range(num_concurrent)]
        
        # Act
        start_time = time.time()
        tasks = [
            agent.process_job_application(
                job["description"],
                resume["text"],
                f"job_{i}",
                f"cand_{i}",
                Mock()  # mock session
            )
            for i, (job, resume) in enumerate(zip(jobs, resumes))
        ]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Assert
        assert len(results) == num_concurrent
        assert total_time < 30  # Should complete in under 30 seconds
        
        # Calculate metrics
        avg_time = total_time / num_concurrent
        assert avg_time < 3  # Average under 3 seconds per evaluation
    
    @pytest.mark.asyncio
    async def test_embedding_generation_speed(self, skill_service):
        """Test: Embedding generation should be fast."""
        skills = ["Python", "JavaScript", "Docker", "Kubernetes", "React"]
        
        start_time = time.time()
        for skill in skills:
            await skill_service.generate_embedding(skill)
        
        total_time = time.time() - start_time
        avg_time = total_time / len(skills)
        
        assert avg_time < 0.5  # Under 500ms per embedding
```

### Test Utilities

```python
# tests/test_utils.py
import time
import functools
from contextlib import contextmanager
from typing import Generator, Any
import logging

logger = logging.getLogger(__name__)

@contextmanager
def assert_performance(max_seconds: float) -> Generator[None, None, None]:
    """Context manager to assert operation completes within time limit."""
    start = time.time()
    yield
    duration = time.time() - start
    assert duration < max_seconds, f"Operation took {duration:.2f}s, max allowed: {max_seconds}s"

def retry_async(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry async functions."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class TestDataBuilder:
    """Builder pattern for complex test data."""
    
    def __init__(self):
        self.data = {}
    
    def with_skills(self, *skills):
        self.data["skills"] = list(skills)
        return self
    
    def with_experience(self, years: int):
        self.data["experience_years"] = years
        return self
    
    def with_education(self, level: str, field: str):
        self.data["education"] = {"level": level, "field": field}
        return self
    
    def build(self):
        return self.data
```

### Testing Best Practices

```python
# Example: Well-structured test with clear phases
class TestBestPractices:
    """Demonstrate testing best practices."""
    
    @pytest.mark.asyncio
    async def test_with_clear_phases(self):
        """Test: Demonstrate Arrange-Act-Assert pattern."""
        # ===== ARRANGE =====
        # Set up all test data and mocks
        test_job = TestDataBuilder() \
            .with_skills("Python", "Docker") \
            .with_experience(5) \
            .build()
        
        mock_service = Mock()
        mock_service.process = AsyncMock(return_value={"score": 0.85})
        
        # ===== ACT =====
        # Execute the operation being tested
        result = await mock_service.process(test_job)
        
        # ===== ASSERT =====
        # Verify the results
        assert result["score"] > 0.8
        mock_service.process.assert_called_once_with(test_job)
    
    def test_with_parametrize(self):
        """Test: Use parametrize for multiple test cases."""
        @pytest.mark.parametrize("input_years,expected_score", [
            (0, 0.0),      # No experience
            (2, 0.4),      # Below minimum
            (5, 0.7),      # Meets minimum
            (8, 1.0),      # Exceeds preferred
            (15, 1.0),     # Way over (capped)
        ])
        def test_experience_scoring(self, agent, input_years, expected_score):
            score = agent._evaluate_experience(
                input_years,
                {"minimum": 5, "preferred": 7}
            )
            assert abs(score - expected_score) < 0.1  # Allow small variance
```

### Test Coverage Goals

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Coverage goals:
# - Overall: >80%
# - Critical paths: >95%
# - Unit tests: 100% of public methods
# - Integration: All API endpoints
# - E2E: Key user workflows
```

### Debugging Test Failures

```python
# tests/debugging_helpers.py
import pytest
import logging
import json
from pathlib import Path

class TestDebugger:
    """Helper for debugging test failures."""
    
    @staticmethod
    def save_test_artifacts(test_name: str, data: dict):
        """Save test data for debugging failures."""
        artifacts_dir = Path("test_artifacts") / test_name
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        with open(artifacts_dir / "data.json", "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    @pytest.fixture
    def capture_logs():
        """Capture logs during test execution."""
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger()
        logger.addHandler(handler)
        yield
        logger.removeHandler(handler)
    
    @staticmethod
    def print_assertion_details(actual, expected, message=""):
        """Print detailed assertion information."""
        print(f"\n{'='*50}")
        print(f"Assertion Failed: {message}")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        print(f"Type Expected: {type(expected)}")
        print(f"Type Actual: {type(actual)}")
        print(f"{'='*50}\n")
```

## Quick Start Guide

### 1. Neon Database Setup

```bash
# Sign up for Neon.tech account (free tier available)
# Create a new project and database
# Get your connection string from Neon console
# It will look like: postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Test connection
psql "$DATABASE_URL" -c "SELECT version();"
```

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/recruitment-poc.git
cd recruitment-poc

# Create virtual environment (Python 3.12+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Start Local Services

```bash
# Only Redis needs to run locally
docker-compose up -d redis

# Verify Redis is running
docker-compose ps
```

### 4. Initialize Database Schema

```bash
# Create a schema.sql file from the database schema section above
# Then run:
psql "$DATABASE_URL" < schema.sql

# Verify tables were created
psql "$DATABASE_URL" -c "\dt"

# Note: Milvus Lite will create its own local file automatically
# No additional setup needed for vector storage
```

### 5. Run the Application

```bash
# Run database migrations
alembic upgrade head

# Start the Chainlit interface
chainlit run src/main.py -w

# In another terminal, start the API server (optional)
uvicorn src.api.main:app --reload
```

### 6. Test the System

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 7. Access the Application

- Chainlit UI: http://localhost:8000
- API Documentation: http://localhost:8001/docs
- Redis Commander: http://localhost:8081 (if added to docker-compose)
- Neon Database Console: https://console.neon.tech

## Demo Workflow

1. **Start Chainlit Interface**
   ```bash
   chainlit run src/main.py
   ```

2. **Upload Job Description and Resume**
   - Click on the file upload button
   - Select a job description file
   - Select a resume file

3. **Or Use Demo Mode**
   - Type "demo" in the chat
   - System will use pre-configured examples

4. **Review Results**
   - See screening and critic scores
   - Review matched and missing skills
   - Check bias flags if any
   - See confidence level

5. **Human Review (if needed)**
   - System will prompt for review when confidence < 85%
   - Choose: Approve, Reject, or Request More Info
   - Provide reasoning for decision

## Key Differences from Full Architecture

| Aspect | Full Architecture (PART_5.md) | POC Implementation |
|--------|------------------------------|-------------------|
| Agent Communication | Message queues (RabbitMQ) | Direct method calls |
| Agent Deployment | Separate containers | Single process |
| State Management | Distributed state | Shared memory + Redis |
| Vector Storage | Dedicated Milvus cluster | Local Milvus Lite file |
| Database | Separate vector + relational | PostgreSQL (Neon) + Milvus Lite |
| Embeddings | Self-hosted models | OpenAI API (text-embedding-3-small) |
| Scalability | Horizontal scaling per agent | Vertical scaling only |
| Fault Tolerance | Agent-level isolation | Process-level only |
| Monitoring | Per-agent metrics | Unified metrics |

## Migration Path to Full System

1. **Extract Agent Classes**: Each method group becomes a separate service
2. **Add Message Queue**: Replace direct calls with async messaging (RabbitMQ)
3. **Scale Vector Storage**: Migrate from Milvus Lite to dedicated Milvus cluster for scale
4. **Containerize Agents**: Deploy each agent as a microservice
5. **Implement Service Mesh**: Add inter-agent communication layer
6. **Scale Horizontally**: Deploy multiple instances of each agent
7. **Add Orchestration**: Kubernetes for container management
8. **Self-host Embeddings**: Replace OpenAI embeddings with local models for cost

## Demo Scenarios

### Scenario 1: Traditional Match
- Software engineer with CS degree applying for developer role
- Expected: High confidence (>0.85), automated approval

### Scenario 2: Hidden Gem
- Self-taught developer with bootcamp background
- Expected: Lower screening score, higher critic score, flagged for review

### Scenario 3: Career Changer
- Data analyst transitioning to data science
- Expected: Strong transferable skills detection, human review recommended

## Today's Implementation Plan

### 🚀 Quick Start Checklist

**Goal**: Working POC that can evaluate candidates by end of day.

#### ✅ Progress Summary
**Completed**: Foundation setup with TDD approach + Core Agent Implementation
- **Database Models**: All models implemented with SQLModel (10 tests ✅)
- **Vector Store Service**: Milvus Lite integration complete (12 tests ✅)  
- **Skill Ontology Service**: Comprehensive skill matching system (10 tests ✅)
- **Redis Service**: State management and caching ready (11 tests ✅)
- **Unified Agent**: Full recruitment workflow orchestration (12 tests ✅)
- **Total Tests Passing**: 55/55 🎉

**Next Steps**: Create API endpoints (Hour 5-6)

### Hour 1-2: Foundation Setup ⏰

1. **Environment & Database** (30 min)
   - [x] Clone repo and create Python 3.12+ virtual environment
   - [x] Install dependencies: `uv pip sync`
   - [x] Copy `.env.example` to `.env` and add API keys
   - [ ] Test Neon connection: `psql "$DATABASE_URL" -c "SELECT version();"`

2. **Initialize Database** (30 min)
   - [x] Create database models with SQLModel (no pgvector extension needed)
   - [x] Implement all database models with comprehensive tests
   - [x] Add proper timestamp handling and relationships
   - [x] **Quick Win**: Database models fully tested (10 tests passing) ✅
   
3. **Start Redis** (15 min)
   - [x] Run: `docker compose up -d redis`
   - [x] Test connection: `docker exec recruitment_redis redis-cli ping`
   - [x] Configure Redis for state management
   - [x] Implement RedisService with full test coverage (11 tests passing)

4. **Create Project Structure** (45 min)
   - [x] Create TDD-based project structure with proper separation of concerns
   - [x] Implement `vector_store.py` with Milvus Lite integration
   - [x] Implement `skill_ontology.py` with comprehensive skill matching
   - [x] **Quick Win**: All services tested (32 total tests passing) ✅

### Hour 3-4: Core Agent Implementation ⏰

5. **Implement UnifiedRecruitmentAgent** (60 min)
   - [x] Create `unified_agent.py` with basic structure
   - [x] Implement `__init__` and `initialize` methods
   - [x] Add `_decompose_job_requirements` (Supervisor)
   - [x] Add `_parse_resume` (Sourcing)
   - [x] **Quick Win**: Parse one job description successfully ✅
   - **Status**: Next task to implement

6. **Implement Matching Logic** (60 min)
   - [x] Add `_semantic_screening` method
   - [x] Add `_critical_review` method
   - [x] Add `_calculate_confidence` method
   - [x] **Quick Win**: Match one candidate to one job ✅

### Hour 5-6: Chainlit UI Integration ⏰

7. **Basic Chainlit Setup** (45 min)
   - [x] Create `main.py` for Chainlit entry point
   - [x] Implement `@cl.on_chat_start` handler
   - [x] Add file upload handling
   - [x] **Quick Win**: "Hello World" in Chainlit UI ✅

8. **Connect Agent to UI** (45 min)
   - [x] Wire up agent initialization
   - [x] Handle job description upload
   - [x] Handle resume upload
   - [x] Display evaluation results
   - [x] **Quick Win**: Complete one evaluation cycle ✅

9. **Add Demo Mode** (30 min) ✅
   - [x] Create sample job description
   - [x] Create sample resume
   - [x] Add "demo" command handler
   - [x] **Quick Win**: Demo evaluation without uploads ✅

### Hour 7-8: Testing & Polish ⏰

10. **Basic Testing** (45 min) ✅
    - [x] Test database connections
    - [x] Test embedding generation
    - [x] Test full evaluation flow
    - [x] Fix any runtime errors

11. **UI Polish** (45 min) ✅
    - [x] Format results nicely
    - [x] Add loading indicators
    - [x] Show matched/missing skills
    - [x] Display confidence scores
    - [x] **Quick Win**: Screenshot-worthy results ✅

12. **Prepare Demo** (30 min) ✅
    - [x] Create 2-3 test scenarios ✅
    - [x] Document how to run the system ✅
    - [x] Record quick demo video ✅
    - [x] Prepare final demo presentation ✅
    - [x] **Final Win**: End-to-end demo ready! 🎉

### 💡 If Time Permits

- Add HITL review flow for low-confidence matches
- Create more comprehensive skill ontology
- Add basic metrics tracking
- Implement bias detection for one category

### 🛑 What We're NOT Doing Today

- Production security (auth, encryption)
- Comprehensive testing suite
- Advanced monitoring/metrics
- Microservice architecture
- Load testing
- CI/CD pipeline

### 📋 Success Criteria

✅ Can upload job description and resume  
✅ System evaluates match with scores  
✅ Shows matched and missing skills  
✅ Displays confidence level  
✅ Works for at least 3 different test cases  
✅ UI is functional (not necessarily pretty)  
✅ Can demo to stakeholders

## 📝 Quick Implementation Notes

### Copy-Paste Helpers

```bash
# Quick environment setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Test database connection
psql "$DATABASE_URL" -c "SELECT version();"

# Install Milvus Lite
pip install milvus-lite pymilvus

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Run Chainlit
chainlit run src/main.py -w
```

### Common Gotchas & Quick Fixes

| Issue | Quick Fix |
|-------|----------|
| Database connection fails | Check SSL mode is 'require' in connection string |
| OpenAI rate limit | Add `time.sleep(0.5)` between API calls |
| Import errors | Make sure to add `__init__.py` in all directories |
| Redis not connecting | Check if port 6379 is already in use |
| Embeddings dimension mismatch | Ensure Milvus collection uses dim=1536 |
| Milvus Lite file grows large | Periodically clean up old embeddings |

### Minimal Working Example

If you get stuck, here's the simplest possible version:

```python
# minimal_poc.py
import os
from openai import OpenAI
import asyncpg
import numpy as np

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def simple_match(job_desc: str, resume: str):
    # Get embeddings
    job_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=job_desc
    ).data[0].embedding
    
    resume_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=resume
    ).data[0].embedding
    
    # Calculate similarity
    similarity = np.dot(job_emb, resume_emb) / (
        np.linalg.norm(job_emb) * np.linalg.norm(resume_emb)
    )
    
    return {"match_score": similarity}
```

### Demo Script for Quick Testing

```python
# quick_demo.py
job = """Python Developer: 3+ years experience, 
FastAPI, Docker, PostgreSQL, REST APIs"""

resume = """John Doe - Software Engineer
4 years Python development
Skills: FastAPI, Docker, PostgreSQL, REST API design
Built microservices handling 1M requests/day"""

# Run: python -m asyncio quick_demo.py
import asyncio
result = asyncio.run(simple_match(job, resume))
print(f"Match Score: {result['match_score']:.2%}")
```

### Next Steps After Today

1. **Tomorrow**: Add HITL flow for <85% confidence matches
2. **This Week**: Expand skill ontology, add more test cases
3. **Next Week**: Performance optimization, batch processing
4. **Future**: Production security, monitoring, scale-out architecture
