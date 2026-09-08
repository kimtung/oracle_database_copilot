"""Repository for ASH (Active Session History) queries."""

from __future__ import annotations

from datetime import datetime

from oracle_mcp.oracle.queries import ash_queries as Q
from oracle_mcp.oracle.repositories.base import BaseRepository


class AshRepository(BaseRepository):

    async def get_ash_sample(
        self,
        begin_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        rows = await self._fetchall(
            Q.ASH_SAMPLE,
            {"begin_time": begin_time, "end_time": end_time},
        )
        return rows

    async def get_ash_sql_activity(
        self,
        sql_id: str,
        begin_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        rows = await self._fetchall(
            Q.ASH_SQL_ACTIVITY,
            {"sql_id": sql_id, "begin_time": begin_time, "end_time": end_time},
        )
        return rows

    async def get_ash_top_sql(
        self,
        begin_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        rows = await self._fetchall(
            Q.ASH_TOP_SQL_IN_RANGE,
            {"begin_time": begin_time, "end_time": end_time},
        )
        return rows

    async def get_sql_wait_events(self, sql_id: str, hours: int = 4) -> list[dict]:
        rows = await self._fetchall(
            Q.SQL_WAIT_EVENTS,
            {"sql_id": sql_id, "hours": hours},
        )
        return rows

    async def get_sql_execution_context(self, sql_id: str, hours: int = 4) -> list[dict]:
        rows = await self._fetchall(
            Q.SQL_EXECUTION_CONTEXT,
            {"sql_id": sql_id, "hours": hours},
        )
        return rows
