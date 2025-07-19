"""Unit tests for vector store service."""
import pytest
import pytest_asyncio
import numpy as np
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from services.vector_store import VectorStoreService, VectorSearchResult


class TestVectorStoreService:
    """Test suite for vector store service."""
    
    @pytest_asyncio.fixture
    async def vector_store(self, mock_config, mock_openai_client):
        """Create vector store service instance."""
        # Use temporary directory for test database
        temp_dir = tempfile.mkdtemp()
        mock_config["milvus_lite_file"] = str(Path(temp_dir) / "test_milvus.db")
        
        service = VectorStoreService(mock_config, mock_openai_client)
        await service.initialize()
        
        yield service
        
        # Cleanup
        await service.close()
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_config, mock_openai_client):
        """Test: Vector store should initialize with collection."""
        # Arrange
        temp_dir = tempfile.mkdtemp()
        mock_config["milvus_lite_file"] = str(Path(temp_dir) / "test_milvus.db")
        
        # Act
        service = VectorStoreService(mock_config, mock_openai_client)
        await service.initialize()
        
        # Assert
        assert service.collection is not None
        assert service.collection_name == mock_config["milvus_collection_name"]
        
        # Cleanup
        await service.close()
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_create_embedding(self, vector_store: VectorStoreService):
        """Test: Should create embeddings for text."""
        # Arrange
        text = "Senior Python Developer with 5 years experience"
        
        # Act
        embedding = await vector_store.create_embedding(text)
        
        # Assert
        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # OpenAI text-embedding-3-small dimension
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_store_resume(self, vector_store: VectorStoreService):
        """Test: Should store resume with embedding."""
        # Arrange
        resume_data = {
            "id": "resume-123",
            "text": "John Doe - Senior Developer with Python expertise",
            "metadata": {
                "candidate_name": "John Doe",
                "skills": ["Python", "FastAPI"],
                "experience_years": 5
            }
        }
        
        # Act
        embedding_id = await vector_store.store_resume(
            resume_data["id"],
            resume_data["text"],
            resume_data["metadata"]
        )
        
        # Assert
        assert embedding_id is not None
        assert isinstance(embedding_id, str)
    
    @pytest.mark.asyncio
    async def test_search_similar_resumes(self, vector_store: VectorStoreService):
        """Test: Should find similar resumes based on job description."""
        # Arrange - Store multiple resumes
        resumes = [
            {
                "id": "resume-1",
                "text": "Python developer with FastAPI and microservices experience",
                "metadata": {"name": "Alice", "skills": ["Python", "FastAPI"]}
            },
            {
                "id": "resume-2",
                "text": "Java developer with Spring Boot expertise",
                "metadata": {"name": "Bob", "skills": ["Java", "Spring"]}
            },
            {
                "id": "resume-3",
                "text": "Python engineer specializing in machine learning",
                "metadata": {"name": "Charlie", "skills": ["Python", "ML"]}
            }
        ]
        
        for resume in resumes:
            await vector_store.store_resume(
                resume["id"],
                resume["text"],
                resume["metadata"]
            )
        
        # Act
        job_description = "Looking for Python developer with FastAPI experience"
        results = await vector_store.search_similar_resumes(
            job_description,
            limit=2
        )
        
        # Assert
        assert len(results) == 2
        assert all(isinstance(r, VectorSearchResult) for r in results)
        assert results[0].score >= results[1].score  # Sorted by score
        # Check that we got relevant results (Alice or Charlie who both have Python)
        result_names = [r.metadata["name"] for r in results]
        assert "Alice" in result_names or "Charlie" in result_names
    
    @pytest.mark.asyncio
    async def test_get_resume_by_id(self, vector_store: VectorStoreService):
        """Test: Should retrieve stored resume by ID."""
        # Arrange
        resume_data = {
            "id": "resume-get-123",
            "text": "Test resume content",
            "metadata": {"name": "Test User"}
        }
        await vector_store.store_resume(
            resume_data["id"],
            resume_data["text"],
            resume_data["metadata"]
        )
        
        # Act
        result = await vector_store.get_resume_by_id(resume_data["id"])
        
        # Assert
        assert result is not None
        assert result.id == resume_data["id"]
        assert result.metadata["name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_update_resume(self, vector_store: VectorStoreService):
        """Test: Should update existing resume."""
        # Arrange
        original_data = {
            "id": "resume-update-123",
            "text": "Original resume content",
            "metadata": {"skills": ["Python"]}
        }
        await vector_store.store_resume(
            original_data["id"],
            original_data["text"],
            original_data["metadata"]
        )
        
        # Act
        updated_text = "Updated resume with more skills"
        updated_metadata = {"skills": ["Python", "Docker", "Kubernetes"]}
        success = await vector_store.update_resume(
            original_data["id"],
            updated_text,
            updated_metadata
        )
        
        # Assert
        assert success is True
        result = await vector_store.get_resume_by_id(original_data["id"])
        assert result.metadata["skills"] == ["Python", "Docker", "Kubernetes"]
    
    @pytest.mark.asyncio
    async def test_delete_resume(self, vector_store: VectorStoreService):
        """Test: Should delete resume from store."""
        # Arrange
        resume_id = "resume-delete-123"
        await vector_store.store_resume(
            resume_id,
            "Resume to be deleted",
            {"name": "Delete Me"}
        )
        
        # Act
        success = await vector_store.delete_resume(resume_id)
        
        # Assert
        assert success is True
        result = await vector_store.get_resume_by_id(resume_id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_batch_store_resumes(self, vector_store: VectorStoreService):
        """Test: Should store multiple resumes efficiently."""
        # Arrange
        resumes = [
            {
                "id": f"batch-resume-{i}",
                "text": f"Resume content for candidate {i}",
                "metadata": {"batch_id": i}
            }
            for i in range(5)
        ]
        
        # Act
        embedding_ids = await vector_store.batch_store_resumes(resumes)
        
        # Assert
        assert len(embedding_ids) == 5
        assert all(isinstance(eid, str) for eid in embedding_ids)
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, vector_store: VectorStoreService):
        """Test: Should filter search results by metadata."""
        # Arrange - Store resumes with different experience levels
        resumes = [
            {
                "id": "junior-1",
                "text": "Junior Python developer",
                "metadata": {"experience_years": 2, "level": "junior"}
            },
            {
                "id": "senior-1",
                "text": "Senior Python developer",
                "metadata": {"experience_years": 8, "level": "senior"}
            },
            {
                "id": "senior-2",
                "text": "Senior Python architect",
                "metadata": {"experience_years": 10, "level": "senior"}
            }
        ]
        
        for resume in resumes:
            await vector_store.store_resume(
                resume["id"],
                resume["text"],
                resume["metadata"]
            )
        
        # Act
        results = await vector_store.search_similar_resumes(
            "Python developer",
            limit=10,
            filter_expr='metadata["level"] == "senior"'
        )
        
        # Assert
        assert len(results) == 2
        assert all(r.metadata["level"] == "senior" for r in results)
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, vector_store: VectorStoreService):
        """Test: Should handle searches with no results."""
        # Act
        results = await vector_store.search_similar_resumes(
            "Quantum computing expert with 20 years experience",
            limit=5
        )
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, vector_store: VectorStoreService):
        """Test: Should handle errors gracefully."""
        # Test invalid embedding dimension
        with pytest.raises(ValueError):
            await vector_store._store_embedding(
                "invalid-id",
                [0.1] * 100,  # Wrong dimension
                {"test": True}
            )
    
    @pytest.mark.asyncio
    async def test_collection_stats(self, vector_store: VectorStoreService):
        """Test: Should provide collection statistics."""
        # Arrange - Add some resumes
        for i in range(3):
            await vector_store.store_resume(
                f"stats-resume-{i}",
                f"Resume {i}",
                {"index": i}
            )
        
        # Act
        stats = await vector_store.get_collection_stats()
        
        # Assert
        assert stats["total_entities"] == 3
        assert stats["collection_name"] == vector_store.collection_name
        assert "index_status" in stats