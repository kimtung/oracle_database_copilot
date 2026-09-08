"""MCP tools — awr.py: get_awr_snapshot, get_awr_sql_stats."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.awr_repo import AwrRepository
from oracle_mcp.security.audit import audit_context


async def get_awr_snapshot(hours: int = 24) -> list[dict]:
    """
    Return AWR snapshot intervals for the given look-back window.

    Useful for identifying snap_id ranges to pass to get_awr_sql_stats.

    Parameters
    ----------
    hours : int
        Look-back window in hours (default 24).

    Sources: DBA_HIST_SNAPSHOT
    """
    args = {"hours": hours}
    async with audit_context(tool="get_awr_snapshot", args=args):
        repo = AwrRepository()
        return await repo.get_awr_snapshots(hours=hours)


async def get_awr_sql_stats(
    sql_id: str,
    days: int = 1,
    begin_snap: int | None = None,
    end_snap: int | None = None,
) -> list[dict]:
    """
    Return per-snapshot execution statistics for a SQL_ID from AWR.

    Use ``days`` for a rolling look-back, or provide ``begin_snap`` /
    ``end_snap`` for a precise snapshot range.

    Parameters
    ----------
    sql_id : str
        Oracle SQL identifier.
    days : int
        Rolling look-back in days (default 1). Ignored if begin_snap/end_snap are set.
    begin_snap : int | None
        Start snapshot ID (inclusive).
    end_snap : int | None
        End snapshot ID (inclusive).

    Sources: DBA_HIST_SQLSTAT, DBA_HIST_SNAPSHOT
    """
    args = {
        "sql_id": sql_id,
        "days": days,
        "begin_snap": begin_snap,
        "end_snap": end_snap,
    }
    async with audit_context(tool="get_awr_sql_stats", args=args):
        repo = AwrRepository()
        if begin_snap is not None and end_snap is not None:
            return await repo.get_awr_sql_stats_by_snap(
                sql_id=sql_id, begin_snap=begin_snap, end_snap=end_snap
            )
        return await repo.get_awr_sql_stats(sql_id=sql_id, days=days)
