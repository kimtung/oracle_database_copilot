import logging

from db_copilot.domain.models.evidence import Evidence
from db_copilot.evidence.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class StorageCollector(BaseCollector):
    """Collects storage metrics (tablespaces), scheduler jobs, and invalid objects."""

    async def collect(self) -> list[Evidence]:
        db_id = await self.get_database_id()
        logger.info(f"Collecting storage & job metrics for database {db_id}")

        # 1. Tablespace usage
        ts_res = await self.mcp.call_tool("get_tablespace_usage", {})
        ts_list = ts_res if isinstance(ts_res, list) else []

        # 2. Failed scheduler jobs (past 24 hours)
        jobs_res = await self.mcp.call_tool("get_failed_jobs", {"hours": 24})
        jobs_list = jobs_res if isinstance(jobs_res, list) else []

        # 3. Invalid objects
        inv_res = await self.mcp.call_tool("get_invalid_objects", {})
        inv_list = inv_res if isinstance(inv_res, list) else []

        evidences: list[Evidence] = []
        evidences.extend(self.normalizer.normalize_tablespace_usage(ts_list))
        evidences.extend(self.normalizer.normalize_failed_jobs(jobs_list))
        evidences.extend(self.normalizer.normalize_invalid_objects(inv_list))

        # Persist normalized evidence items
        for ev in evidences:
            await self.repo.save_evidence(ev)

        logger.info(f"Saved {len(evidences)} storage/job evidence items")
        return evidences
