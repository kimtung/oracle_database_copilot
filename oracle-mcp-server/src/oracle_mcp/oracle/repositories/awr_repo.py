"""Repository for AWR (Automatic Workload Repository) queries."""

from __future__ import annotations

from oracle_mcp.oracle.queries import awr_queries as Q
from oracle_mcp.oracle.repositories.base import BaseRepository


class AwrRepository(BaseRepository):

    async def get_awr_snapshots(self, hours: int = 24) -> list[dict]:
        rows = await self._fetchall(Q.AWR_SNAPSHOTS, {"hours": hours})
        return rows

    async def get_awr_sql_stats(self, sql_id: str, days: int = 1) -> list[dict]:
        rows = await self._fetchall(
            Q.AWR_SQL_STATS,
            {"sql_id": sql_id, "days": days},
        )
        return rows

    async def get_awr_sql_stats_by_snap(
        self,
        sql_id: str,
        begin_snap: int,
        end_snap: int,
    ) -> list[dict]:
        rows = await self._fetchall(
            Q.AWR_SQL_STATS_BY_SNAP,
            {"sql_id": sql_id, "begin_snap": begin_snap, "end_snap": end_snap},
        )
        return rows
