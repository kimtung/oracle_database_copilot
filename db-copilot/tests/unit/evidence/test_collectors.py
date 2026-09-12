from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.db.schema import Base
from db_copilot.domain.enums import EvidenceType
from db_copilot.evidence.collectors import SessionCollector, SqlCollector, StorageCollector
from db_copilot.evidence.repository import EvidenceRepository


@pytest.fixture
async def test_repo():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        repo = EvidenceRepository(session)
        yield repo

    await engine.dispose()


@pytest.mark.asyncio
async def test_sql_collector(test_repo: EvidenceRepository):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool = AsyncMock(
        return_value=[
            {"sql_id": "sql_1", "elapsed_time": 2500, "cpu_time": 1000, "executions": 5},
            {"sql_id": "sql_2", "elapsed_time": 5000, "cpu_time": 4000, "executions": 1},
        ]
    )

    collector = SqlCollector(mcp_client=mock_mcp, repo=test_repo)
    snapshot, metrics = await collector.collect(metric="elapsed_time", limit=10)

    assert snapshot.id is not None
    assert len(metrics) == 2
    mock_mcp.call_tool.assert_awaited_once_with(
        "get_top_sql", {"metric": "elapsed_time", "limit": 10, "hours": 1}
    )


@pytest.mark.asyncio
async def test_session_collector(test_repo: EvidenceRepository):
    mock_mcp = AsyncMock()

    async def mock_call_tool(tool_name, arguments):
        if tool_name == "get_blocking_sessions":
            return {
                "total_blocked": 1,
                "chains": [{"root_blocker_sid": 101, "blocked_sessions": [202]}],
            }
        if tool_name == "get_long_running_sessions":
            return [{"sid": 303, "elapsed_seconds": 3600}]
        return []

    mock_mcp.call_tool = AsyncMock(side_effect=mock_call_tool)

    collector = SessionCollector(mcp_client=mock_mcp, repo=test_repo)
    evidences = await collector.collect()

    assert len(evidences) == 2
    types = {e.type for e in evidences}
    assert EvidenceType.BLOCKING_SESSION in types
    assert EvidenceType.LONG_RUNNING_SESSION in types


@pytest.mark.asyncio
async def test_storage_collector(test_repo: EvidenceRepository):
    mock_mcp = AsyncMock()

    async def mock_call_tool(tool_name, arguments):
        if tool_name == "get_tablespace_usage":
            return [{"name": "APP_TS", "used_pct": 91.5}]
        if tool_name == "get_failed_jobs":
            return [{"job_name": "BACKUP_JOB", "error_message": "ORA-19504"}]
        if tool_name == "get_invalid_objects":
            return [{"owner": "SCHEMA_A", "object_name": "PKG_TEST", "object_type": "PACKAGE"}]
        return []

    mock_mcp.call_tool = AsyncMock(side_effect=mock_call_tool)

    collector = StorageCollector(mcp_client=mock_mcp, repo=test_repo)
    evidences = await collector.collect()

    assert len(evidences) == 3
    types = {e.type for e in evidences}
    assert EvidenceType.TABLESPACE_FULL in types
    assert EvidenceType.JOB_FAILURE in types
    assert EvidenceType.INVALID_OBJECTS in types
