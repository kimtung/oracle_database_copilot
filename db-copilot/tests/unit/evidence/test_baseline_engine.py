from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.db.schema import Base, SqlMetric
from db_copilot.evidence.baseline_engine import BaselineEngine
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


def test_remove_outliers():
    engine = BaselineEngine(repo=None)
    # [100, 102, 98, 101, 100, 10000] has a massive outlier
    values = [100.0, 102.0, 98.0, 101.0, 100.0, 10000.0]
    filtered = engine.remove_outliers(values)
    assert 10000.0 not in filtered
    assert len(filtered) == 5


def test_compute_stats_reliable_vs_unreliable():
    engine = BaselineEngine(repo=None, min_samples=5)

    # 3 samples -> unreliable
    stats_unreliable = engine.compute_stats([100.0, 110.0, 120.0])
    assert stats_unreliable["sample_count"] == 3
    assert stats_unreliable["is_reliable"] is False
    assert stats_unreliable["p50_elapsed_ms"] == 110.0

    # 6 samples -> reliable
    stats_reliable = engine.compute_stats([100.0, 105.0, 110.0, 115.0, 120.0, 125.0])
    assert stats_reliable["sample_count"] == 6
    assert stats_reliable["is_reliable"] is True
    assert stats_reliable["mean_elapsed_ms"] == 112.5


@pytest.mark.asyncio
async def test_recalculate_persists_baselines(test_repo: EvidenceRepository):
    db = await test_repo.get_or_create_default_database()

    # Create metrics for sql_target with matching day & hour
    now = datetime.now(UTC)
    for i in range(6):
        # captured_at on the exact same hour and weekday, 1 day apart or different weeks
        t = now - timedelta(days=7 * i)
        metric = SqlMetric(
            database_id=db.id,
            sql_id="sql_target",
            captured_at=t,
            elapsed_time_ms=200 + i * 10,
        )
        test_repo.session.add(metric)
    await test_repo.session.flush()

    engine = BaselineEngine(repo=test_repo, rolling_days=50, min_samples=5)
    updated = await engine.recalculate(database_id=db.id)
    assert updated >= 1

    baseline = await test_repo.get_baseline(
        database_id=db.id,
        sql_id="sql_target",
        hour_of_day=now.hour,
        day_of_week=now.weekday(),
    )
    assert baseline is not None
    assert baseline.is_reliable is True
    assert float(baseline.mean_elapsed_ms) > 0
