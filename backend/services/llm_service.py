"""
LLM Service - Unified interface for LLM calls via litellm.
Supports streaming, tool calling, structured output, and retry logic.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Optional

import litellm
from litellm import acompletion, aembedding

from backend.config import get_config, LLMConfig

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM service using litellm for multi-provider support."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or get_config().llm
        litellm.set_verbose = False

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[str | dict] = None,
        response_format: Optional[dict] = None,
        stop: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Make a completion call to the LLM.
        
        Args:
            messages: Chat messages in OpenAI format
            model: Model to use (defaults to primary_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: Tool definitions for function calling
            tool_choice: Tool choice strategy
            response_format: Structured output format
            stop: Stop sequences
            
        Returns:
            Full response dict with choices, usage, etc.
        """
        model = model or self.config.primary_model
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": self.config.timeout,
        }

        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        if response_format:
            kwargs["response_format"] = response_format
        if stop:
            kwargs["stop"] = stop

        retries = 3
        for attempt in range(retries):
            try:
                response = await acompletion(**kwargs)
                return response.model_dump()
            except litellm.exceptions.RateLimitError:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, retrying in {wait_time}s (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(wait_time)
            except litellm.exceptions.APIConnectionError as e:
                if attempt < retries - 1:
                    logger.warning(f"API connection error, retrying: {e}")
                    await asyncio.sleep(1)
                else:
                    raise
            except Exception as e:
                logger.error(f"LLM completion error: {e}")
                raise

        raise RuntimeError("Max retries exceeded for LLM completion")

    async def complete_text(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Get just the text content from a completion."""
        response = await self.complete(messages, model=model, **kwargs)
        return response["choices"][0]["message"]["content"] or ""

    async def complete_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict],
        model: Optional[str] = None,
        **kwargs,
    ) -> tuple[str | None, list[dict] | None]:
        """Make a completion call that may invoke tools.
        
        Returns:
            Tuple of (text_content, tool_calls) where tool_calls is a list
            of dicts with 'name' and 'arguments' keys.
        """
        response = await self.complete(messages, tools=tools, model=model, **kwargs)
        message = response["choices"][0]["message"]
        
        text_content = message.get("content")
        tool_calls = None
        
        if message.get("tool_calls"):
            tool_calls = []
            for tc in message["tool_calls"]:
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"]),
                })
        
        return text_content, tool_calls

    async def stream(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream completion tokens."""
        model = model or self.config.primary_model
        
        response = await acompletion(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    async def embed(
        self,
        texts: list[str],
        model: Optional[str] = None,
    ) -> list[list[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        model = model or self.config.embedding_model
        
        response = await aembedding(
            model=model,
            input=texts,
        )
        
        return [item["embedding"] for item in response.data]

    async def embed_single(self, text: str, model: Optional[str] = None) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed([text], model=model)
        return embeddings[0]

    async def structured_output(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        model: Optional[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Get structured JSON output from the LLM.
        
        Args:
            messages: Chat messages
            schema: JSON schema for the response
            model: Model to use
            
        Returns:
            Parsed JSON response matching the schema
        """
        response = await self.complete(
            messages=messages,
            model=model,
            response_format={"type": "json_schema", "json_schema": {"name": "response", "schema": schema}},
            **kwargs,
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)


# Singleton
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the singleton LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
