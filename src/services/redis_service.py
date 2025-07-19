"""Redis service for state management and caching."""
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import redis.asyncio as redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisService:
    """Service for managing Redis connections and operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Redis service."""
        self.config = config
        self.client: Optional[Redis] = None
        self.channel = config.get("redis_channel", "hitl_queue")
    
    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            self.client = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                password=self.config.get("redis_password", ""),
                decode_responses=True
            )
            
            # Test connection
            await self.client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def set_workflow_state(
        self,
        workflow_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Store workflow state."""
        key = f"workflow:{workflow_id}"
        state_json = json.dumps(state)
        await self.client.hset(key, "state", state_json)
        await self.client.hset(key, "updated_at", datetime.now(timezone.utc).isoformat())
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow state."""
        key = f"workflow:{workflow_id}"
        state_json = await self.client.hget(key, "state")
        if state_json:
            return json.loads(state_json)
        return None
    
    async def publish_hitl_request(
        self,
        request_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Publish human-in-the-loop request."""
        message = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        await self.client.publish(self.channel, json.dumps(message))
        logger.info(f"Published HITL request: {request_id}")
    
    async def add_to_evaluation_queue(
        self,
        job_id: str,
        resume_id: str,
        priority: int = 0
    ) -> None:
        """Add evaluation to processing queue."""
        score = -priority  # Redis sorts ascending, we want high priority first
        member = f"{job_id}:{resume_id}"
        await self.client.zadd("evaluation_queue", {member: score})
    
    async def get_next_evaluation(self) -> Optional[Tuple[str, str]]:
        """Get next evaluation from queue."""
        items = await self.client.zrange("evaluation_queue", 0, 0)
        if items:
            item = items[0]
            await self.client.zrem("evaluation_queue", item)
            job_id, resume_id = item.split(":")
            return job_id, resume_id
        return None
    
    async def cache_embedding(
        self,
        text_hash: str,
        embedding: List[float],
        ttl: int = 86400  # 24 hours
    ) -> None:
        """Cache text embedding."""
        key = f"embedding:{text_hash}"
        await self.client.setex(
            key,
            ttl,
            json.dumps(embedding)
        )
    
    async def get_cached_embedding(self, text_hash: str) -> Optional[List[float]]:
        """Retrieve cached embedding."""
        key = f"embedding:{text_hash}"
        embedding_json = await self.client.get(key)
        if embedding_json:
            return json.loads(embedding_json)
        return None
    
    async def increment_metric(self, metric_name: str) -> int:
        """Increment a metric counter."""
        key = f"metric:{metric_name}"
        return await self.client.hincrby("metrics", metric_name, 1)
    
    async def get_metrics(self) -> Dict[str, int]:
        """Get all metrics."""
        metrics = await self.client.hgetall("metrics")
        return {k: int(v) for k, v in metrics.items()}