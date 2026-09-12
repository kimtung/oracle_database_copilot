from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from db_copilot.api.app import create_app
from db_copilot.api.deps import get_db_session
from db_copilot.config.settings import get_settings


@pytest.fixture(autouse=True)
def disable_scheduler_for_tests(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENABLE_SCHEDULER", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    # Mock execute returns truthy result for check_db_connection
    session.execute = AsyncMock(return_value=True)
    return session


@pytest.fixture
async def client(mock_db_session: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
