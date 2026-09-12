from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.db.schema import Base, SqlBaseline
from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.evidence.repository import EvidenceRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_repository_get_or_create_database(async_session: AsyncSession):
    repo = EvidenceRepository(async_session)
    db1 = await repo.get_or_create_default_database("DB_PROD", "10.0.0.1", "ORCL", "19c")
    assert db1.name == "DB_PROD"
    assert db1.id is not None

    # Calling again returns existing database
    db2 = await repo.get_or_create_default_database("DB_PROD")
    assert db2.id == db1.id


@pytest.mark.asyncio
async def test_repository_create_snapshot_and_metrics(async_session: AsyncSession):
    repo = EvidenceRepository(async_session)
    db = await repo.get_or_create_default_database()

    snapshot = await repo.create_snapshot(
        database_id=db.id,
        active_sessions=15,
        blocking_sessions=2,
        cpu_pct=45.5,
        health_score=85,
    )
    assert snapshot.id is not None
    assert snapshot.active_sessions == 15

    metrics_data = [
        {"sql_id": "sql_1", "elapsed_time": 1200, "cpu_time": 800, "executions": 10},
        {"sql_id": "sql_2", "elapsed_time": 4500, "cpu_time": 3000, "executions": 2},
    ]
    saved = await repo.save_sql_metrics(metrics_data, database_id=db.id, snapshot_id=snapshot.id)
    assert len(saved) == 2

    active_ids = await repo.get_active_sql_ids(db.id, days=1)
    assert "sql_1" in active_ids
    assert "sql_2" in active_ids

    history = await repo.get_sql_metrics_history(db.id, "sql_1", days=1)
    assert len(history) == 1
    assert history[0].elapsed_time_ms == 1200


@pytest.mark.asyncio
async def test_repository_baseline_upsert_and_get(async_session: AsyncSession):
    repo = EvidenceRepository(async_session)
    db = await repo.get_or_create_default_database()

    baseline = SqlBaseline(
        database_id=db.id,
        sql_id="sql_abc",
        hour_of_day=14,
        day_of_week=2,
        sample_count=8,
        mean_elapsed_ms=150.0,
        stddev_elapsed_ms=20.0,
        p50_elapsed_ms=145.0,
        p95_elapsed_ms=180.0,
        is_reliable=True,
        calculated_at=datetime.now(UTC),
    )
    await repo.upsert_baseline(baseline)

    fetched = await repo.get_baseline(db.id, "sql_abc", hour_of_day=14, day_of_week=2)
    assert fetched is not None
    assert float(fetched.mean_elapsed_ms) == 150.0
    assert fetched.is_reliable is True

    # Test update existing
    baseline.mean_elapsed_ms = 160.0
    await repo.upsert_baseline(baseline)
    updated = await repo.get_baseline(db.id, "sql_abc", hour_of_day=14, day_of_week=2)
    assert float(updated.mean_elapsed_ms) == 160.0


@pytest.mark.asyncio
async def test_repository_save_evidence_and_audit(async_session: AsyncSession):
    repo = EvidenceRepository(async_session)
    db = await repo.get_or_create_default_database()

    ev = Evidence(
        type=EvidenceType.BLOCKING_SESSION,
        source="V$SESSION",
        entity_type="SESSION",
        entity_id="sid_123",
        severity=Severity.HIGH,
        data={"wait_event": "enq: TX - row lock contention"},
    )
    saved_ev = await repo.save_evidence(ev)
    assert saved_ev.id == ev.id
    assert saved_ev.type == "blocking_session"

    audit = await repo.log_mcp_audit(
        tool_name="get_top_sql",
        input_args={"limit": 10},
        duration_ms=45,
        rows_returned=10,
        database_id=db.id,
    )
    assert audit.id is not None
    assert audit.tool_name == "get_top_sql"
    assert audit.duration_ms == 45
