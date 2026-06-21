# litellm stub

class RateLimitError(Exception):
    pass

class APIConnectionError(Exception):
    pass

async def acompletion(**kwargs):
    """Return a minimal stub mimicking litellm's async completion response."""
    class Response:
        def model_dump(self):
            return {
                "choices": [{"message": {"content": "stub completion"}}],
                "usage": {}
            }
    return Response()

async def aembedding(**kwargs):
    """Return a minimal stub for embeddings."""
    class EmbeddingResponse:
        def __init__(self):
            self.data = [{"embedding": [0.0, 0.0, 0.0]}]
    return EmbeddingResponse()

__all__ = ["RateLimitError", "APIConnectionError", "acompletion", "aembedding"]
