"""
Memory Manager - Manages short-term, long-term, and episodic memory for agents.
Uses Redis for short-term, Qdrant for long-term semantic, and PostgreSQL for episodic.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from backend.services.llm_service import get_llm_service
from backend.services.vector_store import get_vector_store
from backend.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)


class MemoryManager:
    """Unified memory manager for agent memory systems."""

    def __init__(self, agent_id: str, session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.session_id = session_id or str(uuid4())
        self.llm = get_llm_service()
        self.vector_store = get_vector_store()
        self.cache = get_cache_service()
        self._short_term: list[dict[str, Any]] = []

    # ── Short-term Memory (conversation context) ──────────────────────

    def add_message(self, role: str, content: str, metadata: Optional[dict] = None) -> None:
        """Add a message to short-term memory."""
        entry = {
            "id": str(uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self._short_term.append(entry)

    def get_messages(self, last_n: Optional[int] = None) -> list[dict[str, str]]:
        """Get messages in OpenAI chat format."""
        messages = self._short_term
        if last_n:
            messages = messages[-last_n:]
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def get_context_window(self, max_tokens: int = 4096) -> list[dict[str, str]]:
        """Get messages that fit within a token budget (rough estimate)."""
        messages = []
        token_count = 0
        for m in reversed(self._short_term):
            estimated_tokens = len(m["content"]) // 4
            if token_count + estimated_tokens > max_tokens:
                break
            messages.insert(0, {"role": m["role"], "content": m["content"]})
            token_count += estimated_tokens
        return messages

    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self._short_term.clear()

    # ── Long-term Memory (semantic search) ────────────────────────────

    async def store_long_term(
        self,
        content: str,
        metadata: Optional[dict] = None,
        collection: Optional[str] = None,
    ) -> str:
        """Store content in long-term semantic memory.
        
        Args:
            content: Text content to store
            metadata: Additional metadata
            collection: Qdrant collection name
            
        Returns:
            ID of the stored memory
        """
        collection = collection or f"agent_{self.agent_id}_memory"
        
        await self.vector_store.ensure_collection(collection)
        
        embedding = await self.llm.embed_single(content)
        
        payload = {
            "content": content,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }
        
        ids = await self.vector_store.upsert(
            collection_name=collection,
            vectors=[embedding],
            payloads=[payload],
        )
        
        return ids[0]

    async def search_long_term(
        self,
        query: str,
        limit: int = 5,
        collection: Optional[str] = None,
        score_threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Search long-term memory semantically.
        
        Args:
            query: Search query
            limit: Max results
            collection: Collection to search
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant memory entries
        """
        collection = collection or f"agent_{self.agent_id}_memory"
        
        query_embedding = await self.llm.embed_single(query)
        
        results = await self.vector_store.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
        
        return results

    # ── Episodic Memory (task/event history) ──────────────────────────

    async def store_episode(
        self,
        event_type: str,
        data: dict[str, Any],
        outcome: Optional[str] = None,
    ) -> str:
        """Store an episodic memory (task execution, decision, etc.)."""
        episode_id = str(uuid4())
        episode = {
            "id": episode_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        cache_key = f"episode:{self.agent_id}:{episode_id}"
        await self.cache.set_json(cache_key, episode, ttl=86400)  # 24h
        
        # Also store in a list for the session
        list_key = f"episodes:{self.agent_id}:{self.session_id}"
        episodes = await self.cache.get_json(list_key) or []
        episodes.append(episode)
        await self.cache.set_json(list_key, episodes, ttl=86400)
        
        return episode_id

    async def get_episodes(
        self,
        event_type: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Retrieve episodic memories for the current session."""
        list_key = f"episodes:{self.agent_id}:{self.session_id}"
        episodes = await self.cache.get_json(list_key) or []
        
        if event_type:
            episodes = [e for e in episodes if e["event_type"] == event_type]
        
        return episodes[-limit:]

    # ── Shared Memory (cross-agent communication) ─────────────────────

    async def share(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> None:
        """Share data with other agents via Redis."""
        cache_key = f"shared:{key}"
        await self.cache.set_json(cache_key, {
            "value": value,
            "from_agent": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, ttl=ttl)

    async def retrieve_shared(self, key: str) -> Optional[Any]:
        """Retrieve shared data from another agent."""
        cache_key = f"shared:{key}"
        data = await self.cache.get_json(cache_key)
        if data:
            return data["value"]
        return None

    async def publish_event(self, event_type: str, data: dict) -> None:
        """Publish an event for other agents to consume."""
        await self.cache.publish(f"agent_events:{event_type}", {
            "from_agent": self.agent_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
