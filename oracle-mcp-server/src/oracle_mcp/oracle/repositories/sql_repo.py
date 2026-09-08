"""Repository for SQL, Session, and Database Info queries."""

from __future__ import annotations

from oracle_mcp.models.response_models import (
    BlockedSession,
    BlockingChain,
    BlockingResult,
    DatabaseInfo,
    LongRunningSession,
    Session,
    SqlStatistics,
    SqlSummary,
)
from oracle_mcp.oracle.queries import sql_queries as Q
from oracle_mcp.oracle.repositories.base import BaseRepository

# Metric → query mapping for get_top_sql
_TOP_SQL_QUERIES: dict[str, str] = {
    "elapsed_time": Q.TOP_SQL_BY_ELAPSED,
    "cpu":          Q.TOP_SQL_BY_CPU,
    "io":           Q.TOP_SQL_BY_IO,
    "buffer_gets":  Q.TOP_SQL_BY_BUFFER_GETS,
    "executions":   Q.TOP_SQL_BY_EXECUTIONS,
}

_VALID_METRICS = frozenset(_TOP_SQL_QUERIES)


class SqlRepository(BaseRepository):

    # ── Database Info ─────────────────────────────────────────────────────

    async def get_database_info(self) -> DatabaseInfo:
        row = await self._fetchone(Q.DATABASE_INFO)
        if row is None:
            raise RuntimeError("Could not query V$DATABASE / V$INSTANCE")
        return DatabaseInfo(**row)

    # ── Top SQL ───────────────────────────────────────────────────────────

    async def get_top_sql(
        self,
        metric: str = "elapsed_time",
        limit: int = 20,
        hours: int = 1,
    ) -> list[SqlSummary]:
        if metric not in _VALID_METRICS:
            raise ValueError(
                f"Invalid metric '{metric}'. Valid values: {sorted(_VALID_METRICS)}"
            )
        rows = await self._fetchall(
            _TOP_SQL_QUERIES[metric],
            {"limit": limit, "hours": hours},
        )
        return [SqlSummary(**row) for row in rows]

    # ── SQL Statistics ────────────────────────────────────────────────────

    async def get_sql_statistics(self, sql_id: str) -> SqlStatistics | None:
        row = await self._fetchone(Q.SQL_STATISTICS, {"sql_id": sql_id})
        if row is None:
            return None
        return SqlStatistics(**row)

    # ── Active Sessions ───────────────────────────────────────────────────

    async def get_active_sessions(self, min_elapsed_sec: int = 0) -> list[Session]:
        rows = await self._fetchall(
            Q.ACTIVE_SESSIONS,
            {"min_elapsed_sec": min_elapsed_sec},
        )
        return [Session(**row) for row in rows]

    # ── Blocking Sessions ─────────────────────────────────────────────────

    async def get_blocking_sessions(self) -> BlockingResult:
        rows = await self._fetchall(Q.BLOCKING_SESSIONS)

        # Group by blocker sid
        chains: dict[int, BlockingChain] = {}
        for row in rows:
            b_sid = row["blocker_sid"]
            if b_sid not in chains:
                chains[b_sid] = BlockingChain(
                    blocker_sid=b_sid,
                    blocker_serial=row.get("blocker_serial", 0),
                    blocker_user=row.get("blocker_user"),
                    blocker_sql_id=row.get("blocker_sql_id"),
                    blocker_wait_event=row.get("blocker_wait_event"),
                    blocker_elapsed_sec=row.get("blocker_elapsed_sec", 0),
                    blocked_sessions=[],
                )
            chains[b_sid].blocked_sessions.append(
                BlockedSession(
                    blocked_sid=row["blocked_sid"],
                    blocked_serial=row.get("blocked_serial", 0),
                    blocked_user=row.get("blocked_user"),
                    blocked_sql_id=row.get("blocked_sql_id"),
                    blocked_wait_event=row.get("blocked_wait_event"),
                    blocked_wait_sec=row.get("blocked_wait_sec", 0),
                )
            )

        chain_list = list(chains.values())
        total_blocked = sum(len(c.blocked_sessions) for c in chain_list)
        max_wait = max(
            (s.blocked_wait_sec for c in chain_list for s in c.blocked_sessions),
            default=0,
        )
        return BlockingResult(
            blocking_chains=chain_list,
            total_blocked=total_blocked,
            max_wait_seconds=max_wait,
        )

    # ── Long-running Sessions ─────────────────────────────────────────────

    async def get_long_running_sessions(
        self, min_minutes: int = 60
    ) -> list[LongRunningSession]:
        rows = await self._fetchall(
            Q.LONG_RUNNING_SESSIONS,
            {"min_seconds": min_minutes * 60},
        )
        return [LongRunningSession(**row) for row in rows]
