import logging

from db_copilot.domain.models.evidence import Evidence
from db_copilot.evidence.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class SessionCollector(BaseCollector):
    """Collects active sessions, blocking chains, and long-running sessions."""

    async def collect(self) -> list[Evidence]:
        db_id = await self.get_database_id()
        logger.info(f"Collecting session data for database {db_id}")

        # 1. Blocking sessions
        blocking_res = await self.mcp.call_tool("get_blocking_sessions", {})
        blocking_data = blocking_res if isinstance(blocking_res, dict) else {"total_blocked": 0}

        # 2. Long running sessions
        long_running_res = await self.mcp.call_tool("get_long_running_sessions", {})
        long_running_sessions = long_running_res if isinstance(long_running_res, list) else []

        evidences: list[Evidence] = []
        evidences.extend(self.normalizer.normalize_blocking_chain(blocking_data))
        evidences.extend(self.normalizer.normalize_long_running_sessions(long_running_sessions))

        # Persist normalized evidence items
        for ev in evidences:
            await self.repo.save_evidence(ev)

        logger.info(f"Saved {len(evidences)} session-related evidence items")
        return evidences
