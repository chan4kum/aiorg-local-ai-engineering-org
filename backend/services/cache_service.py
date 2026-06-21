"""
Cache Service - In-memory caching, pub/sub, and rate limiting (formerly Redis).
"""

import json
import logging
import asyncio
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    """In-memory cache service for OpenClaw."""

    def __init__(self):
        self._store = {}
        self._expiry = {}
        self._queues = {}
        self._lock = asyncio.Lock()

    def _cleanup(self):
        """Clean up expired keys."""
        now = time.time()
        expired = [k for k, v in self._expiry.items() if v < now]
        for k in expired:
            self._store.pop(k, None)
            self._expiry.pop(k, None)

    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        async with self._lock:
            self._cleanup()
            return self._store.get(key)

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
        async with self._lock:
            self._store[key] = str(value)
            if ttl:
                self._expiry[key] = time.time() + ttl
            else:
                self._expiry.pop(key, None)

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
        async with self._lock:
            self._store.pop(key, None)
            self._expiry.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        async with self._lock:
            self._cleanup()
            return key in self._store

    async def publish(self, channel: str, message: dict) -> None:
        """Publish a message to an in-memory channel."""
        async with self._lock:
            if channel not in self._queues:
                self._queues[channel] = []
        
        msg_str = json.dumps(message, default=str)
        # Fan-out to all subscribers
        for queue in self._queues.get(channel, []):
            await queue.put(msg_str)

    async def subscribe(self, channel: str):
        """Subscribe to a channel. Yields messages."""
        queue = asyncio.Queue()
        async with self._lock:
            if channel not in self._queues:
                self._queues[channel] = []
            self._queues[channel].append(queue)
            
        try:
            while True:
                msg_str = await queue.get()
                yield json.loads(msg_str)
        finally:
            async with self._lock:
                if channel in self._queues:
                    self._queues[channel].remove(queue)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomic increment."""
        async with self._lock:
            self._cleanup()
            val = self._store.get(key, "0")
            try:
                new_val = int(val) + amount
            except ValueError:
                new_val = amount
            self._store[key] = str(new_val)
            return new_val

    async def rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """Simple sliding window rate limiter. Returns True if allowed."""
        async with self._lock:
            self._cleanup()
            current = self._store.get(key)
            if current is None:
                self._store[key] = "1"
                self._expiry[key] = time.time() + window_seconds
                return True
            if int(current) < max_requests:
                self._store[key] = str(int(current) + 1)
                return True
            return False

    async def close(self):
        """Cleanup."""
        pass


_cache_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """Get or create singleton cache service."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
