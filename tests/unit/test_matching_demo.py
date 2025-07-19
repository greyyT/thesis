"""Demo test to show matching logic works."""
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

from agents.unified_agent import UnifiedRecruitmentAgent, EvaluationResult


@pytest.mark.asyncio
async def test_matching_logic_demo(mock_config, mock_openai_client):
    """Demo: Full matching logic workflow."""
    with patch('agents.unified_agent.VectorStoreService') as mock_vector, \
         patch('agents.unified_agent.SkillOntologyService') as mock_skill, \
         patch('agents.unified_agent.RedisService') as mock_redis:
        
        # Setup mocks
        mock_vector_instance = Mock()
        mock_vector_instance.initialize = AsyncMock()
        mock_vector_instance.create_embedding = AsyncMock(return_value=[0.1] * 1536)
        mock_vector.return_value = mock_vector_instance
        
        mock_skill_instance = Mock()
        mock_skill_instance.normalize_skill = Mock(side_effect=lambda x: x.lower())
        mock_skill_instance.extract_skills_from_text = Mock(return_value=["Python", "FastAPI"])
        mock_skill_instance.calculate_skill_similarity = Mock(return_value=0.85)
        mock_skill_instance.get_related_skills = Mock(return_value=["Flask"])
        mock_skill.return_value = mock_skill_instance
        
        mock_redis_instance = Mock()
        mock_redis_instance.initialize = AsyncMock()
        mock_redis_instance.set_workflow_state = AsyncMock()
        mock_redis_instance.increment_metric = AsyncMock()
        mock_redis_instance.publish_hitl_request = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        
        # Create agent
        agent = UnifiedRecruitmentAgent(mock_config, mock_openai_client)
        await agent.initialize()
        
        # Setup LLM mock
        agent.llm = Mock()
        agent.llm.chat = Mock()
        agent.llm.chat.completions = Mock()
        agent.llm.chat.completions.create = AsyncMock()
        
        # Test data
        job_description = """
        Senior Python Developer
        
        Requirements:
        - 5+ years Python experience
        - Strong FastAPI knowledge
        - Docker and Kubernetes
        - PostgreSQL experience
        """
        
        resume_text = """
        John Doe
        Python Developer - 6 years experience
        
        Skills: Python, FastAPI, Docker, SQL
        
        Experience:
        - Built REST APIs with FastAPI
        - Deployed applications with Docker
        - Worked with PostgreSQL databases
        """
        
        # Mock all agent methods to test the full flow
        agent._init_workflow_state = AsyncMock(return_value="workflow_demo")
        
        # Mock job decomposition
        agent._decompose_job_requirements = AsyncMock(return_value={
            "technical_skills": ["python", "fastapi", "docker", "kubernetes", "postgresql"],
            "experience_years": {"minimum": 5, "preferred": 7},
            "skill_embeddings": {
                "python": [0.1] * 1536,
                "fastapi": [0.2] * 1536
            }
        })
        
        # Mock resume parsing
        agent._parse_resume = AsyncMock(return_value={
            "skills": {"technical": ["python", "fastapi", "docker", "sql"]},
            "total_experience_years": 6.0,
            "resume_embedding": [0.15] * 1536
        })
        
        # Let the real methods run
        agent._semantic_screening = agent.__class__._semantic_screening.__get__(agent)
        agent._critical_review = agent.__class__._critical_review.__get__(agent)
        agent._calculate_confidence = agent.__class__._calculate_confidence.__get__(agent)
        
        # Mock critical review LLM response
        critic_response = Mock()
        critic_response.choices = [Mock(message=Mock(content=json.dumps({
            "adjusted_score": 0.82,
            "confidence_in_assessment": 0.90,
            "bias_flags": [],
            "hidden_gem_indicators": [],
            "transferable_skills": [
                {"from": "sql", "to": "postgresql", "relevance": 0.9}
            ],
            "reasoning": "Strong match with transferable SQL skills"
        })))]
        
        agent._log_evaluation = AsyncMock()
        agent._generate_explanation = AsyncMock(return_value="Good match: 4/5 skills matched, experience meets requirements")
        
        # Run the full evaluation
        async def mock_create(*args, **kwargs):
            # Return critic response for critical review call
            messages = kwargs.get("messages", [])
            if messages and "Review this candidate evaluation" in messages[0]["content"]:
                return critic_response
            # Default response
            return Mock(choices=[Mock(message=Mock(content=""))])
        
        agent.llm.chat.completions.create = AsyncMock(side_effect=mock_create)
        
        result = await agent.process_job_application(
            job_description, resume_text, "job_demo", "cand_demo"
        )
        
        # Assertions
        assert isinstance(result, EvaluationResult)
        print(f"\n✅ Screening Score: {result.screening_score:.2%}")
        print(f"✅ Critic Score: {result.critic_score:.2%}")
        print(f"✅ Confidence: {result.confidence:.2%}")
        print(f"✅ Needs Review: {result.needs_review}")
        print(f"✅ Matched Skills: {len(result.matched_skills)}")
        print(f"✅ Missing Skills: {result.missing_skills}")
        print(f"✅ Explanation: {result.explanation}")
        
        # Verify the matching logic worked
        assert result.screening_score > 0.7  # Good match
        assert result.critic_score > 0.8  # Critic found transferable skills
        assert len(result.matched_skills) >= 3  # At least 3 skills matched
        assert "kubernetes" in result.missing_skills  # Correctly identified missing skill
        
        return result


if __name__ == "__main__":
    # Can run this directly to see the demo
    import asyncio
    from conftest import mock_config, mock_openai_client
    
    config = mock_config()
    client = mock_openai_client()
    
    result = asyncio.run(test_matching_logic_demo(config, client))
    print("\n🎉 Matching logic is working correctly!")