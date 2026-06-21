# Stub for google.generativeai module

# This stub provides minimal functionality required by the project
# It defines configure, types.GenerationConfig, GenerativeModel, and its generate_content method.

_api_key = None

def configure(api_key: str):
    """Stub configure function storing the API key (no-op)."""
    global _api_key
    _api_key = api_key

class _GenerationConfig:
    def __init__(self, *, temperature: float = 0.0, max_output_tokens: int = None):
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

class types:
    GenerationConfig = _GenerationConfig

class _GenerationResult:
    def __init__(self, text: str = "stub response"):
        self.text = text
        # Provide dummy usage_metadata similar to real response
        self.usage_metadata = {
            "prompt_token_count": 0,
            "candidates_token_count": 0,
            "total_token_count": 0,
        }

class GenerativeModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_content(self, prompt: str, *, generation_config=None):
        # Return a stub result with the prompt echoed or fixed text
        return _GenerationResult(text=f"stub response for prompt: {prompt}")

# Export symbols
__all__ = ["configure", "types", "GenerativeModel"]
