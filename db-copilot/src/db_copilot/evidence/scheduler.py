import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db_copilot.config.settings import get_settings
from db_copilot.db.session import get_sessionmaker
from db_copilot.evidence.baseline_engine import BaselineEngine
from db_copilot.evidence.collectors import SessionCollector, SqlCollector, StorageCollector
from db_copilot.evidence.repository import EvidenceRepository
from db_copilot.mcp.client import OracleMcpClient

logger = logging.getLogger(__name__)


class EvidenceScheduler:
    """Manages scheduled background jobs for evidence collection and baseline recalculation."""

    def __init__(self, scheduler: AsyncIOScheduler | None = None):
        self.scheduler = scheduler or AsyncIOScheduler()
        self.settings = get_settings()

    async def run_sql_collection(self) -> None:
        try:
            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                repo = EvidenceRepository(session)
                mcp = OracleMcpClient()
                collector = SqlCollector(mcp, repo)
                await collector.collect()
                await session.commit()
        except Exception as e:
            logger.error(f"Scheduled SQL collection failed: {e}", exc_info=True)

    async def run_session_collection(self) -> None:
        try:
            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                repo = EvidenceRepository(session)
                mcp = OracleMcpClient()
                collector = SessionCollector(mcp, repo)
                await collector.collect()
                await session.commit()
        except Exception as e:
            logger.error(f"Scheduled session collection failed: {e}", exc_info=True)

    async def run_storage_collection(self) -> None:
        try:
            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                repo = EvidenceRepository(session)
                mcp = OracleMcpClient()
                collector = StorageCollector(mcp, repo)
                await collector.collect()
                await session.commit()
        except Exception as e:
            logger.error(f"Scheduled storage collection failed: {e}", exc_info=True)

    async def run_baseline_recalculation(self) -> None:
        try:
            sessionmaker = get_sessionmaker()
            async with sessionmaker() as session:
                repo = EvidenceRepository(session)
                db = await repo.get_or_create_default_database()
                engine = BaselineEngine(repo)
                await engine.recalculate(db.id)
                await session.commit()
        except Exception as e:
            logger.error(f"Scheduled baseline recalculation failed: {e}", exc_info=True)

    def register_jobs(self) -> None:
        interval_min = self.settings.collection_interval_minutes
        recalc_hr = self.settings.baseline_recalc_interval_hours

        self.scheduler.add_job(
            self.run_sql_collection,
            "interval",
            minutes=interval_min,
            id="sql_collector",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_session_collection,
            "interval",
            minutes=interval_min,
            id="session_collector",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_storage_collection,
            "interval",
            minutes=interval_min,
            id="storage_collector",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_baseline_recalculation,
            "interval",
            hours=recalc_hr,
            id="baseline_recalc",
            replace_existing=True,
        )

    def start(self) -> None:
        self.register_jobs()
        self.scheduler.start()
        logger.info("EvidenceScheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("EvidenceScheduler stopped")
