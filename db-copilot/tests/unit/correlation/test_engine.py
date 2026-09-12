from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.config.settings import Settings
from db_copilot.correlation.engine import CorrelationEngine
from db_copilot.correlation.repository import IncidentRepository
from db_copilot.db.schema import Base
from db_copilot.domain.enums import IncidentCategory, Severity


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_mcp():
    mcp = AsyncMock()
    mcp.call_tool = AsyncMock(return_value=[])
    return mcp


@pytest.mark.asyncio
async def test_correlation_engine_creates_incident_with_hypotheses(
    async_session: AsyncSession, mock_mcp
):
    repo = IncidentRepository(async_session)
    settings = Settings(tablespace_critical_threshold=90.0)
    engine = CorrelationEngine(repository=repo, mcp_client=mock_mcp, settings=settings)

    collected_data = {
        "tablespaces": [
            {"tablespace_name": "DATA_TS", "used_pct": 96.0, "free_bytes": 1024 * 1024 * 5}
        ]
    }

    incidents = await engine.correlate(collected_data)
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.category == IncidentCategory.TABLESPACE
    assert inc.severity == Severity.CRITICAL
    assert inc.diagnosis is not None
    assert "H4: Resource Capacity Exhaustion" in inc.diagnosis.primary_cause
    assert inc.diagnosis.confidence >= 0.50


@pytest.mark.asyncio
async def test_correlation_engine_deduplication(async_session: AsyncSession, mock_mcp):
    repo = IncidentRepository(async_session)
    settings = Settings(long_running_threshold_sec=1800)
    engine = CorrelationEngine(repository=repo, mcp_client=mock_mcp, settings=settings)

    collected_data = {
        "active_sessions": [
            {"sid": 999, "elapsed_seconds": 3600, "username": "APP_USER", "sql_id": "sql_loop"}
        ]
    }

    # First run creates new incident
    incidents_first = await engine.correlate(collected_data)
    assert len(incidents_first) == 1
    first_id = incidents_first[0].id

    # Second run with same session data correlates to existing incident
    incidents_second = await engine.correlate(collected_data)
    assert len(incidents_second) == 1
    assert incidents_second[0].id == first_id

    # Check that database only has 1 incident
    all_open = await repo.list_incidents()
    assert len(all_open) == 1
