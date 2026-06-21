import os
import sys
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient

# Ensure the root project directory is on the path so that backend, agents, etc. can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now we can safely import our app and config
from backend.main import app
from backend.config import get_config

from unittest.mock import patch, AsyncMock, MagicMock
from contextlib import asynccontextmanager

@pytest.fixture(scope="session")
def test_app():
    """Yields the FastAPI app with mocked background services."""
    # Directly attach mocked services to app.state for tests
    app.state.event_bus = MagicMock()
    app.state.event_bus.publish = AsyncMock()
    app.state.task_queue = MagicMock()
    app.state.task_queue.enqueue = AsyncMock()
    yield app

@pytest.fixture(scope="module")
def client(test_app) -> TestClient:
    """TestClient fixture for calling API endpoints."""
    with TestClient(test_app) as c:
        yield c

