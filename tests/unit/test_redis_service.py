"""Unit tests for Redis service."""
import pytest
import pytest_asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
import hashlib

from services.redis_service import RedisService


class TestRedisService:
    """Test suite for Redis service."""
    
    @pytest_asyncio.fixture
    async def redis_service(self, mock_config):
        """Create Redis service instance with mock client."""
        service = RedisService(mock_config)
        
        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_client.hset = AsyncMock()
        mock_client.hget = AsyncMock()
        mock_client.hgetall = AsyncMock(return_value={})
        mock_client.publish = AsyncMock()
        mock_client.zadd = AsyncMock()
        mock_client.zrange = AsyncMock(return_value=[])
        mock_client.zrem = AsyncMock()
        mock_client.setex = AsyncMock()
        mock_client.get = AsyncMock()
        mock_client.hincrby = AsyncMock(return_value=1)
        mock_client.close = AsyncMock()
        
        # Inject mock client
        with patch('redis.asyncio.Redis', return_value=mock_client):
            await service.initialize()
            service.client = mock_client
        
        yield service
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_config):
        """Test: Redis service should initialize connection."""
        # Arrange
        service = RedisService(mock_config)
        
        # Mock Redis
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_redis.return_value = mock_client
            
            # Act
            await service.initialize()
            
            # Assert
            mock_redis.assert_called_once_with(
                host=mock_config["redis_host"],
                port=mock_config["redis_port"],
                password="",
                decode_responses=True
            )
            mock_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_workflow_state(self, redis_service: RedisService):
        """Test: Should store workflow state in Redis."""
        # Arrange
        workflow_id = "workflow-123"
        state = {
            "stage": "screening",
            "status": "in_progress",
            "data": {"score": 0.85}
        }
        
        # Act
        await redis_service.set_workflow_state(workflow_id, state)
        
        # Assert
        key = f"workflow:{workflow_id}"
        redis_service.client.hset.assert_any_call(
            key, "state", json.dumps(state)
        )
        # Check that updated_at was set
        calls = redis_service.client.hset.call_args_list
        assert len(calls) == 2
        assert calls[1][0][0] == key
        assert calls[1][0][1] == "updated_at"
    
    @pytest.mark.asyncio
    async def test_get_workflow_state(self, redis_service: RedisService):
        """Test: Should retrieve workflow state from Redis."""
        # Arrange
        workflow_id = "workflow-123"
        state = {"stage": "screening", "status": "completed"}
        redis_service.client.hget = AsyncMock(return_value=json.dumps(state))
        
        # Act
        result = await redis_service.get_workflow_state(workflow_id)
        
        # Assert
        redis_service.client.hget.assert_called_once_with(
            f"workflow:{workflow_id}", "state"
        )
        assert result == state
    
    @pytest.mark.asyncio
    async def test_get_workflow_state_not_found(self, redis_service: RedisService):
        """Test: Should return None for non-existent workflow."""
        # Arrange
        redis_service.client.hget = AsyncMock(return_value=None)
        
        # Act
        result = await redis_service.get_workflow_state("nonexistent")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_publish_hitl_request(self, redis_service: RedisService):
        """Test: Should publish HITL request to channel."""
        # Arrange
        request_id = "hitl-123"
        data = {
            "type": "review_required",
            "confidence": 0.75,
            "reason": "Low confidence score"
        }
        
        # Act
        await redis_service.publish_hitl_request(request_id, data)
        
        # Assert
        redis_service.client.publish.assert_called_once()
        channel, message = redis_service.client.publish.call_args[0]
        assert channel == redis_service.channel
        
        # Verify message structure
        message_data = json.loads(message)
        assert message_data["request_id"] == request_id
        assert message_data["data"] == data
        assert "timestamp" in message_data
    
    @pytest.mark.asyncio
    async def test_evaluation_queue_operations(self, redis_service: RedisService):
        """Test: Should add and retrieve evaluations from queue."""
        # Test adding to queue
        await redis_service.add_to_evaluation_queue("job-1", "resume-1", priority=1)
        redis_service.client.zadd.assert_called_once_with(
            "evaluation_queue", {"job-1:resume-1": -1}
        )
        
        # Test getting from queue
        redis_service.client.zrange = AsyncMock(return_value=["job-2:resume-2"])
        result = await redis_service.get_next_evaluation()
        
        assert result == ("job-2", "resume-2")
        redis_service.client.zrange.assert_called_once_with("evaluation_queue", 0, 0)
        redis_service.client.zrem.assert_called_once_with(
            "evaluation_queue", "job-2:resume-2"
        )
    
    @pytest.mark.asyncio
    async def test_empty_evaluation_queue(self, redis_service: RedisService):
        """Test: Should return None for empty queue."""
        # Arrange
        redis_service.client.zrange = AsyncMock(return_value=[])
        
        # Act
        result = await redis_service.get_next_evaluation()
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_embedding_cache_operations(self, redis_service: RedisService):
        """Test: Should cache and retrieve embeddings."""
        # Test caching
        text_hash = hashlib.sha256("test text".encode()).hexdigest()
        embedding = [0.1, 0.2, 0.3, 0.4]
        
        await redis_service.cache_embedding(text_hash, embedding, ttl=3600)
        redis_service.client.setex.assert_called_once_with(
            f"embedding:{text_hash}",
            3600,
            json.dumps(embedding)
        )
        
        # Test retrieval
        redis_service.client.get = AsyncMock(return_value=json.dumps(embedding))
        result = await redis_service.get_cached_embedding(text_hash)
        
        assert result == embedding
        redis_service.client.get.assert_called_once_with(f"embedding:{text_hash}")
    
    @pytest.mark.asyncio
    async def test_cached_embedding_not_found(self, redis_service: RedisService):
        """Test: Should return None for cache miss."""
        # Arrange
        redis_service.client.get = AsyncMock(return_value=None)
        
        # Act
        result = await redis_service.get_cached_embedding("nonexistent")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_metrics_operations(self, redis_service: RedisService):
        """Test: Should increment and retrieve metrics."""
        # Test increment
        redis_service.client.hincrby = AsyncMock(return_value=5)
        count = await redis_service.increment_metric("resumes_processed")
        
        assert count == 5
        redis_service.client.hincrby.assert_called_once_with(
            "metrics", "resumes_processed", 1
        )
        
        # Test get all metrics
        redis_service.client.hgetall = AsyncMock(return_value={
            "resumes_processed": "10",
            "jobs_created": "5",
            "evaluations_completed": "8"
        })
        
        metrics = await redis_service.get_metrics()
        assert metrics == {
            "resumes_processed": 10,
            "jobs_created": 5,
            "evaluations_completed": 8
        }
    
    @pytest.mark.asyncio
    async def test_close_connection(self, redis_service: RedisService):
        """Test: Should close Redis connection properly."""
        # Act
        await redis_service.close()
        
        # Assert
        redis_service.client.close.assert_called_once()