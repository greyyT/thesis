"""Unit tests for unified recruitment agent."""
import pytest
import pytest_asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
from datetime import datetime, timezone
import numpy as np

from agents.unified_agent import UnifiedRecruitmentAgent, EvaluationResult


class TestUnifiedRecruitmentAgent:
    """Test the main recruitment agent functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for agent."""
        return {
            "openai_api_key": "test-key",
            "database_url": "postgresql://test",
            "milvus_lite_file": "./test_milvus.db",
            "redis_host": "localhost",
            "redis_port": 6379,
            "hitl_confidence_threshold": 0.85,
            "embedding_dimension": 1536
        }
    
    @pytest_asyncio.fixture
    async def agent(self, mock_config, mock_openai_client):
        """Create agent with mocked dependencies."""
        with patch('agents.unified_agent.VectorStoreService') as mock_vector, \
             patch('agents.unified_agent.SkillOntologyService') as mock_skill, \
             patch('agents.unified_agent.RedisService') as mock_redis:
            
            # Create mock instances
            mock_vector_instance = Mock()
            mock_vector_instance.initialize = AsyncMock()
            mock_vector_instance.create_embedding = AsyncMock(return_value=[0.1] * 1536)
            mock_vector_instance.search_similar_resumes = AsyncMock(return_value=[])
            mock_vector.return_value = mock_vector_instance
            
            mock_skill_instance = Mock()
            mock_skill_instance.normalize_skill = Mock(side_effect=lambda x: x.lower())
            mock_skill_instance.extract_skills_from_text = Mock(return_value=["Python", "FastAPI"])
            mock_skill_instance.calculate_skill_similarity = Mock(return_value=0.75)
            mock_skill_instance.get_related_skills = Mock(return_value=[])
            mock_skill.return_value = mock_skill_instance
            
            mock_redis_instance = Mock()
            mock_redis_instance.initialize = AsyncMock()
            mock_redis_instance.set_workflow_state = AsyncMock()
            mock_redis_instance.increment_metric = AsyncMock()
            mock_redis_instance.publish_hitl_request = AsyncMock()
            mock_redis.return_value = mock_redis_instance
            
            agent = UnifiedRecruitmentAgent(mock_config, mock_openai_client)
            await agent.initialize()
            
            # Make chat completions work
            agent.llm.chat = Mock()
            agent.llm.chat.completions = Mock()
            agent.llm.chat.completions.create = AsyncMock()
            
            yield agent
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_config, mock_openai_client):
        """Test: Agent should initialize all services."""
        # Arrange
        with patch('agents.unified_agent.VectorStoreService') as mock_vector, \
             patch('agents.unified_agent.SkillOntologyService') as mock_skill, \
             patch('agents.unified_agent.RedisService') as mock_redis:
            
            # Setup mock instances
            mock_vector_instance = Mock()
            mock_vector_instance.initialize = AsyncMock()
            mock_vector.return_value = mock_vector_instance
            
            mock_redis_instance = Mock()
            mock_redis_instance.initialize = AsyncMock()
            mock_redis.return_value = mock_redis_instance
            
            # Act
            agent = UnifiedRecruitmentAgent(mock_config, mock_openai_client)
            await agent.initialize()
            
            # Assert
            mock_vector.assert_called_once()
            mock_skill.assert_called_once()
            mock_redis.assert_called_once()
            mock_vector_instance.initialize.assert_called_once()
            mock_redis_instance.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_job_requirement_decomposition(self, agent: UnifiedRecruitmentAgent):
        """Test: Should correctly decompose job requirements."""
        # Arrange
        job_description = "Senior Python Developer, 5+ years, FastAPI experience required"
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps({
            "technical_skills": ["Python", "FastAPI"],
            "experience_years": {"minimum": 5, "preferred": 7},
            "education": {"level": "Bachelor's", "fields": ["Computer Science"]},
            "soft_skills": ["Communication", "Leadership"],
            "domain": ["Web Development"],
            "nice_to_have": ["Docker", "Kubernetes"]
        })))]
        
        agent.llm.chat.completions.create = AsyncMock(return_value=mock_response)
        agent.vector_store.create_embedding = AsyncMock(return_value=[0.1] * 1536)
        
        # Act
        result = await agent._decompose_job_requirements(job_description, "workflow_123")
        
        # Assert
        assert result["technical_skills"] == ["python", "fastapi"]  # Normalized
        assert result["experience_years"]["minimum"] == 5
        assert result["experience_years"]["preferred"] == 7
        assert result["soft_skills"] == ["communication", "leadership"]
        assert "skill_embeddings" in result
        assert len(result["skill_embeddings"]) == 2
    
    @pytest.mark.asyncio
    async def test_resume_parsing(self, agent: UnifiedRecruitmentAgent):
        """Test: Should extract structured data from resume."""
        # Arrange
        resume_text = """John Doe
        Senior Python Developer - 6 years experience
        
        Skills: Python, FastAPI, Docker, PostgreSQL
        
        Experience:
        - Senior Python Developer at TechCorp (3 years)
        - Python Developer at StartupXYZ (3 years)
        
        Education: BS Computer Science
        """
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps({
            "skills": {
                "technical": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                "soft": ["Problem Solving", "Team Leadership"]
            },
            "experience": [
                {
                    "company": "TechCorp",
                    "title": "Senior Python Developer",
                    "duration": "3 years",
                    "achievements": ["Built scalable APIs", "Led team of 5"]
                },
                {
                    "company": "StartupXYZ",
                    "title": "Python Developer",
                    "duration": "3 years",
                    "achievements": ["Developed microservices"]
                }
            ],
            "education": [{
                "degree": "Bachelor's",
                "field": "Computer Science",
                "institution": "State University"
            }],
            "certifications": [],
            "projects": []
        })))]
        
        agent.llm.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Act
        result = await agent._parse_resume(resume_text, "workflow_123")
        
        # Assert
        assert "python" in result["skills"]["technical"]  # Normalized
        assert "fastapi" in result["skills"]["technical"]
        assert result["total_experience_years"] == 6.0
        assert len(result["experience"]) == 2
        assert result["education"][0]["degree"] == "Bachelor's"
    
    @pytest.mark.asyncio
    async def test_semantic_screening(self, agent: UnifiedRecruitmentAgent):
        """Test: Should perform semantic matching between job and resume."""
        # Arrange
        job_requirements = {
            "technical_skills": ["python", "fastapi", "docker"],
            "experience_years": {"minimum": 3, "preferred": 5},
            "skill_embeddings": {"python": [0.1] * 1536, "fastapi": [0.2] * 1536}
        }
        
        parsed_resume = {
            "skills": {"technical": ["python", "fastapi", "flask"]},
            "total_experience_years": 4.0,
            "resume_embedding": [0.15] * 1536
        }
        
        # Mock vector search
        agent.vector_store.search_similar_resumes = AsyncMock(return_value=[
            Mock(score=0.85, metadata={"skill": "python"}),
            Mock(score=0.80, metadata={"skill": "fastapi"})
        ])
        
        # Mock skill matching
        agent.skill_service.calculate_skill_similarity = Mock(return_value=0.75)
        
        # Act
        result = await agent._semantic_screening(
            job_requirements, parsed_resume, "workflow_123"
        )
        
        # Assert
        assert result["score"] > 0.7
        assert len(result["matched_skills"]) >= 2
        assert result["missing_skills"] == ["docker"]
        assert result["experience_match"] == True
    
    @pytest.mark.asyncio
    async def test_critical_review(self, agent: UnifiedRecruitmentAgent):
        """Test: Should perform critical review with bias detection."""
        # Arrange
        screening_result = {
            "score": 0.65,
            "matched_skills": [
                {"required": "python", "found": "python", "confidence": 0.9}
            ],
            "missing_skills": ["docker"]
        }
        
        parsed_resume = {
            "education": [],  # No formal education
            "skills": {"technical": ["python", "self-taught", "bootcamp"]}
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps({
            "adjusted_score": 0.78,
            "confidence_in_assessment": 0.85,
            "bias_flags": ["non_traditional_education"],
            "hidden_gem_indicators": ["self_taught_success", "practical_experience"],
            "transferable_skills": [
                {"from": "flask", "to": "fastapi", "relevance": 0.8}
            ],
            "reasoning": "Strong practical skills despite non-traditional background"
        })))]
        
        agent.llm.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Act
        result = await agent._critical_review(
            screening_result, parsed_resume, {}, "workflow_123"
        )
        
        # Assert
        assert result["score"] == 0.78
        assert result["bias_flags"] == ["non_traditional_education"]
        assert result["hidden_gem"] == True
        assert len(result["transferable_skills"]) > 0
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, agent: UnifiedRecruitmentAgent):
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
        assert abs(confidence_metrics["score_difference"] - 0.05) < 0.0001  # Handle floating point precision
        assert confidence_metrics["review_type"] == "none"
    
    @pytest.mark.asyncio
    async def test_hidden_gem_detection(self, agent: UnifiedRecruitmentAgent):
        """Test: Should identify hidden gem candidates."""
        # Arrange
        screening_result = {"score": 0.35}
        critic_result = {
            "score": 0.75,
            "confidence_in_assessment": 0.85,
            "bias_flags": ["non_traditional_education"],
            "hidden_gem": True,
            "transferable_skills": [
                {"from": "data_analysis", "to": "data_science", "relevance": 0.8}
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
    async def test_full_evaluation_workflow(self, agent: UnifiedRecruitmentAgent):
        """Test: Should complete full evaluation workflow."""
        # Arrange
        job_desc = "Senior Python Developer with FastAPI experience"
        resume = "John Doe, Python expert with 5 years experience"
        
        # Mock workflow state
        agent._init_workflow_state = AsyncMock(return_value="workflow_123")
        
        # Mock all sub-methods
        agent._decompose_job_requirements = AsyncMock(return_value={
            "technical_skills": ["python", "fastapi"],
            "experience_years": {"minimum": 3}
        })
        agent._parse_resume = AsyncMock(return_value={
            "skills": {"technical": ["python", "fastapi"]},
            "total_experience_years": 5
        })
        agent._semantic_screening = AsyncMock(return_value={
            "score": 0.85,
            "matched_skills": [
                {"required": "python", "found": "python", "confidence": 1.0},
                {"required": "fastapi", "found": "fastapi", "confidence": 0.9}
            ],
            "missing_skills": []
        })
        agent._critical_review = AsyncMock(return_value={
            "score": 0.88,
            "bias_flags": [],
            "hidden_gem": False,
            "transferable_skills": [],
            "confidence_in_assessment": 0.95  # Add this for proper confidence calculation
        })
        agent._log_evaluation = AsyncMock()
        agent._generate_explanation = AsyncMock(return_value="Strong match with all requirements")
        
        # Act
        result = await agent.process_job_application(
            job_desc, resume, "job_123", "cand_456"
        )
        
        # Assert
        assert isinstance(result, EvaluationResult)
        assert result.screening_score == 0.85
        assert result.critic_score == 0.88
        assert not result.needs_review
        assert result.explanation == "Strong match with all requirements"
        assert len(result.matched_skills) == 2
        assert len(result.missing_skills) == 0
    
    def test_experience_parsing_edge_cases(self, agent: UnifiedRecruitmentAgent):
        """Test: Should handle various experience formats."""
        assert agent._parse_duration("5 years") == 5.0
        assert agent._parse_duration("2 years 6 months") == 2.5
        assert agent._parse_duration("6 months") == 0.5
        assert agent._parse_duration("18 months") == 1.5
        assert agent._parse_duration("1 year") == 1.0
        assert agent._parse_duration("no experience") == 0.0
        assert agent._parse_duration("10+ years") == 10.0


class TestAgentErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest_asyncio.fixture
    async def agent(self, mock_config, mock_openai_client):
        """Create agent for error testing."""
        with patch('agents.unified_agent.VectorStoreService') as mock_vector, \
             patch('agents.unified_agent.SkillOntologyService') as mock_skill, \
             patch('agents.unified_agent.RedisService') as mock_redis:
            
            # Setup mock instances
            mock_vector_instance = Mock()
            mock_vector_instance.initialize = AsyncMock()
            mock_vector_instance.create_embedding = AsyncMock(return_value=[0.1] * 1536)
            mock_vector.return_value = mock_vector_instance
            
            mock_skill_instance = Mock()
            mock_skill_instance.normalize_skill = Mock(side_effect=lambda x: x.lower())
            mock_skill.return_value = mock_skill_instance
            
            mock_redis_instance = Mock()
            mock_redis_instance.initialize = AsyncMock()
            mock_redis_instance.set_workflow_state = AsyncMock()
            mock_redis.return_value = mock_redis_instance
            
            agent = UnifiedRecruitmentAgent(mock_config, mock_openai_client)
            
            # Setup LLM mock
            agent.llm = Mock()
            agent.llm.chat = Mock()
            agent.llm.chat.completions = Mock()
            agent.llm.chat.completions.create = AsyncMock()
            
            yield agent
    
    @pytest.mark.asyncio
    async def test_llm_failure_handling(self, agent: UnifiedRecruitmentAgent):
        """Test: Should handle LLM failures gracefully."""
        # Arrange
        agent.llm.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await agent._decompose_job_requirements("test job", "workflow_123")
        assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, agent: UnifiedRecruitmentAgent):
        """Test: Should handle invalid JSON from LLM."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON"))]
        agent.llm.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            await agent._decompose_job_requirements("test job", "workflow_123")
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, agent: UnifiedRecruitmentAgent):
        """Test: Should handle missing fields in parsed data."""
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps({
            "technical_skills": ["Python"]
            # Missing other required fields
        })))]
        agent.llm.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Act
        result = await agent._decompose_job_requirements("test job", "workflow_123")
        
        # Assert - Should have defaults
        assert "experience_years" in result
        assert result["experience_years"]["minimum"] == 0