# src/openclaw/api_client.py
"""Unified API client for LLM calls.

Selects the appropriate provider (Google AI SDK, DeepSeek, Ollama via litellm)
based on the `DEFAULT_LLM_PROVIDER` environment variable.
"""

import os
import logging
from typing import Any, List, Optional
import asyncio
import requests
logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
_litellm = None
_google_ai = None

def _load_litellm():
    global _litellm
    if _litellm is None:
        try:
            import litellm
            _litellm = litellm
        except ImportError as e:
            logger.error("litellm is not installed: %s", e)
            raise
    return _litellm

def _load_google_ai():
    global _google_ai
    if _google_ai is None:
        try:
            import google.generativeai as genai
            _google_ai = genai
        except ImportError as e:
            logger.error("google-generativeai is not installed: %s", e)
            raise
    return _google_ai

class APIClient:
    """High‑level wrapper that delegates to the selected provider.

    The provider is chosen at runtime based on the `DEFAULT_LLM_PROVIDER`
    environment variable. Supported values:
    - "google": uses the Google Gemini SDK (`google.generativeai`).
    - "litellm": falls back to the existing litellm configuration.
    - any other value defaults to litellm.
    """

    def __init__(self):
        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "litellm").lower()
        logger.info("APIClient initialized with provider %s", self.provider)

    async def completion(
        self,
        *,
        model: str,
        messages: List[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[dict]] = None,
        tool_choice: Optional[Any] = None,
        response_format: Optional[dict] = None,
        stop: Optional[List[str]] = None,
        **extra,
    ) -> dict:
        """Generate a completion using the configured provider.

        The return shape mirrors litellm's response for compatibility.
        """
        if self.provider == "google":
            return await self._google_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra,
            )
        elif self.provider == "deepseek":
            return await self._deepseek_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra,
            )
        else:
            litellm = _load_litellm()
            return await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format,
                stop=stop,
                **extra,
            )

    async def embedding(self, *, model: str, input: List[str]) -> dict:
        """Generate embeddings using the selected provider."""
        if self.provider == "google":
            litellm = _load_litellm()
            return await litellm.aembedding(model=model, input=input)
        else:
            litellm = _load_litellm()
            return await litellm.aembedding(model=model, input=input)

    async def _google_completion(
        self,
        *,
        model: str,
        messages: List[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra,
    ) -> dict:
        """Call Google Gemini via `google.generativeai`.

        The Gemini SDK is synchronous, so we run it in a thread to keep the API async.
        """
        genai = _load_google_ai()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set in environment")
        genai.configure(api_key=api_key)

        prompt = "\n".join(
            f"{msg.get('role', '').title()}: {msg.get('content', '')}" for msg in messages
        )
        generation_config = genai.types.GenerationConfig(
            temperature=temperature or 0.0,
            max_output_tokens=max_tokens,
        )

        def _call():
            model_instance = genai.GenerativeModel(model_name=model)
            return model_instance.generate_content(prompt, generation_config=generation_config)

        response = await asyncio.to_thread(_call)
        return {
            "choices": [
                {
                    "message": {"content": response.text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": getattr(response, "usage_metadata", {}).get("prompt_token_count", 0),
                "completion_tokens": getattr(response, "usage_metadata", {}).get("candidates_token_count", 0),
                "total_tokens": getattr(response, "usage_metadata", {}).get("total_token_count", 0),
            }
        }

    async def _deepseek_completion(
        self,
        *,
        model: str,
        messages: List[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **extra,
    ) -> dict:
        """Call DeepSeek via HTTP POST.

        Uses the DEEPSEEK_API_KEY environment variable.
        Returns a dict compatible with litellm response shape.
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set in environment")
        url = "https://api.deepseek.com/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **extra,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        def _call():
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        response = await asyncio.to_thread(_call)
        # Adapt DeepSeek response to litellm-like shape
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"choices": [{"message": {"content": content}}], "usage": {}}
