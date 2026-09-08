"""MCP tools — sql.py: get_top_sql, get_sql_statistics, get_sql_wait_events, get_sql_execution_context."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.ash_repo import AshRepository
from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.security.audit import audit_context


async def get_top_sql(
    metric: str = "elapsed_time",
    limit: int = 20,
    hours: int = 1,
) -> list[dict]:
    """
    Return the top SQL statements ranked by the chosen performance metric.

    Parameters
    ----------
    metric : str
        Ranking dimension. One of:
        ``elapsed_time`` | ``cpu`` | ``io`` | ``buffer_gets`` | ``executions``
    limit : int
        Maximum number of rows to return (default 20, max 100).
    hours : int
        Look-back window in hours (default 1).

    Sources: V$SQLSTATS
    """
    limit = min(limit, 100)
    args = {"metric": metric, "limit": limit, "hours": hours}

    async with audit_context(tool="get_top_sql", args=args):
        repo = SqlRepository()
        results = await repo.get_top_sql(metric=metric, limit=limit, hours=hours)
        return [r.model_dump(mode="json") for r in results]


async def get_sql_statistics(sql_id: str) -> dict | None:
    """
    Return cumulative execution statistics for a specific SQL_ID.

    Parameters
    ----------
    sql_id : str
        Oracle SQL identifier (up to 13 characters).

    Sources: V$SQL (real-time cumulative stats)
    Returns None if the SQL_ID is not found in the shared pool.
    """
    args = {"sql_id": sql_id}
    async with audit_context(tool="get_sql_statistics", args=args):
        repo = SqlRepository()
        result = await repo.get_sql_statistics(sql_id)
        if result is None:
            return None
        return result.model_dump(mode="json")


async def get_sql_wait_events(sql_id: str, hours: int = 4) -> list[dict]:
    """
    Return aggregated wait events for a specific SQL_ID in the given time window.

    Parameters
    ----------
    sql_id : str
        Oracle SQL identifier.
    hours : int
        Look-back window in hours (default 4).

    Returns event name, wait class, count, total/avg/max wait time.
    Sources: V$ACTIVE_SESSION_HISTORY
    """
    args = {"sql_id": sql_id, "hours": hours}
    async with audit_context(tool="get_sql_wait_events", args=args):
        repo = AshRepository()
        return await repo.get_sql_wait_events(sql_id=sql_id, hours=hours)


async def get_sql_execution_context(sql_id: str, hours: int = 4) -> list[dict]:
    """
    Return the calling context (module, action, program, machine) for a SQL_ID.

    Identifies which application component is executing this SQL and how often.
    Sources: V$ACTIVE_SESSION_HISTORY
    """
    args = {"sql_id": sql_id, "hours": hours}
    async with audit_context(tool="get_sql_execution_context", args=args):
        repo = AshRepository()
        return await repo.get_sql_execution_context(sql_id=sql_id, hours=hours)
