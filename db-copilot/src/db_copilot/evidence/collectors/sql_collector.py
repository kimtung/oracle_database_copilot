import logging
from datetime import UTC, datetime

from db_copilot.db.schema import Snapshot, SqlMetric
from db_copilot.evidence.collectors.base import BaseCollector

logger = logging.getLogger(__name__)


class SqlCollector(BaseCollector):
    """Periodically collects Top SQL metrics from Oracle and creates a snapshot."""

    async def collect(
        self, metric: str = "elapsed_time", limit: int = 100, hours: int = 1
    ) -> tuple[Snapshot, list[SqlMetric]]:
        db_id = await self.get_database_id()
        logger.info(f"Collecting Top SQL metrics for database {db_id}")

        raw_top_sql = await self.mcp.call_tool(
            "get_top_sql",
            {"metric": metric, "limit": limit, "hours": hours},
        )
        raw_list = raw_top_sql if isinstance(raw_top_sql, list) else []

        snapshot = await self.repo.create_snapshot(
            database_id=db_id,
            captured_at=datetime.now(UTC),
            raw_data={"top_sql_count": len(raw_list), "query_metric": metric},
        )

        saved_metrics = await self.repo.save_sql_metrics(
            raw_list, database_id=db_id, snapshot_id=snapshot.id
        )
        logger.info(f"Saved {len(saved_metrics)} SQL metrics for snapshot {snapshot.id}")
        return snapshot, saved_metrics
