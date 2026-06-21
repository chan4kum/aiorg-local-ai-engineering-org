import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock

# We need to set the environment variable before APIClient is instantiated or test it carefully
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "litellm")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

@pytest.mark.asyncio
@patch("openclaw.api_client._load_litellm")
async def test_apiclient_default_provider(mock_load_litellm, mock_env, monkeypatch):
    # We patch os.environ directly for this test
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "litellm")
    
    from openclaw.api_client import APIClient
    
    # Mock litellm module
    mock_litellm = MagicMock()
    mock_litellm.acompletion = AsyncMock(return_value={"choices": [{"message": {"content": "Hello litellm"}}]})
    mock_load_litellm.return_value = mock_litellm
    
    client = APIClient()
    assert client.provider == "litellm"
    
    response = await client.completion(
        model="test-model",
        messages=[{"role": "user", "content": "Hi"}]
    )
    
    assert response["choices"][0]["message"]["content"] == "Hello litellm"
    mock_litellm.acompletion.assert_called_once()


@pytest.mark.asyncio
@patch("openclaw.api_client._load_google_ai")
async def test_apiclient_google_provider(mock_load_google_ai, mock_env, monkeypatch):
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "google")
    
    from openclaw.api_client import APIClient
    
    # Mock google generative ai
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello Google"
    # generate_content is synchronous in APIClient thread
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    mock_load_google_ai.return_value = mock_genai
    
    client = APIClient()
    assert client.provider == "google"
    
    response = await client.completion(
        model="gemini-pro",
        messages=[{"role": "user", "content": "Hi"}]
    )
    
    assert response["choices"][0]["message"]["content"] == "Hello Google"
    mock_genai.GenerativeModel.assert_called_once_with(model_name="gemini-pro")
