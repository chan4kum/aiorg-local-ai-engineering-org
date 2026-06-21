"""
Cache Service - Redis-based caching, pub/sub, and rate limiting.
"""

import json
import logging
from typing import Any, Optional

from backend.config import get_config, RedisConfig

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based cache service for OpenClaw."""

    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or get_config().redis
        self._client = None

    async def _get_client(self):
        """Lazy-initialize Redis async client."""
        if self._client is None:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.from_url(
                    self.config.url,
                    decode_responses=True,
                )
            except ImportError:
                logger.warning("redis package not installed")
                raise
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        client = await self._get_client()
        return await client.get(key)

    async def get_json(self, key: str) -> Optional[dict]:
        """Get and deserialize a JSON value."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None,
    ) -> None:
        """Set a value with optional TTL in seconds."""
        client = await self._get_client()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Serialize and set a JSON value."""
        await self.set(key, json.dumps(value, default=str), ttl=ttl)

    async def delete(self, key: str) -> None:
        """Delete a key."""
        client = await self._get_client()
        await client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        client = await self._get_client()
        return bool(await client.exists(key))

    async def publish(self, channel: str, message: dict) -> None:
        """Publish a message to a Redis channel."""
        client = await self._get_client()
        await client.publish(channel, json.dumps(message, default=str))

    async def subscribe(self, channel: str):
        """Subscribe to a Redis channel. Yields messages."""
        client = await self._get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"])
        finally:
            await pubsub.unsubscribe(channel)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomic increment."""
        client = await self._get_client()
        return await client.incrby(key, amount)

    async def rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """Simple sliding window rate limiter. Returns True if allowed."""
        client = await self._get_client()
        current = await client.get(key)
        if current is None:
            await client.setex(key, window_seconds, 1)
            return True
        if int(current) < max_requests:
            await client.incr(key)
            return True
        return False

    async def close(self):
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create singleton cache service."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
