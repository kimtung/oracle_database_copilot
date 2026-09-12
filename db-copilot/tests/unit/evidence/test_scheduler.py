from unittest.mock import patch

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db_copilot.evidence.scheduler import EvidenceScheduler


def test_scheduler_jobs_registration():
    scheduler_backend = AsyncIOScheduler()
    ev_scheduler = EvidenceScheduler(scheduler=scheduler_backend)

    ev_scheduler.register_jobs()

    jobs = scheduler_backend.get_jobs()
    job_ids = {j.id for j in jobs}
    assert "sql_collector" in job_ids
    assert "session_collector" in job_ids
    assert "storage_collector" in job_ids
    assert "baseline_recalc" in job_ids


@pytest.mark.asyncio
async def test_scheduler_start_and_shutdown():
    import asyncio

    scheduler_backend = AsyncIOScheduler()
    ev_scheduler = EvidenceScheduler(scheduler=scheduler_backend)

    ev_scheduler.start()
    assert scheduler_backend.running is True

    ev_scheduler.shutdown()
    await asyncio.sleep(0.05)
    assert scheduler_backend.running is False


@pytest.mark.asyncio
async def test_scheduler_run_sql_collection_safe_on_error():
    scheduler_backend = AsyncIOScheduler()
    ev_scheduler = EvidenceScheduler(scheduler=scheduler_backend)

    with patch(
        "db_copilot.evidence.scheduler.get_sessionmaker",
        side_effect=Exception("DB pool failed"),
    ):
        # Should catch exception internally and not raise
        await ev_scheduler.run_sql_collection()
        await ev_scheduler.run_session_collection()
        await ev_scheduler.run_storage_collection()
        await ev_scheduler.run_baseline_recalculation()
