"""MCP tools — ash.py: get_ash_sample, get_ash_sql_activity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from oracle_mcp.oracle.repositories.ash_repo import AshRepository
from oracle_mcp.security.audit import audit_context


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def get_ash_sample(
    begin_time: str | None = None,
    end_time: str | None = None,
    hours: int = 1,
) -> list[dict]:
    """
    Return ASH samples from V$ACTIVE_SESSION_HISTORY for the given time range.

    Parameters
    ----------
    begin_time : str | None
        ISO-8601 datetime string (e.g. "2026-09-08T14:00:00"). If None,
        defaults to ``now - hours``.
    end_time : str | None
        ISO-8601 datetime string. If None, defaults to now.
    hours : int
        Convenience shortcut when begin_time/end_time are not provided.

    Sources: V$ACTIVE_SESSION_HISTORY
    """
    now = _now_utc()
    end_dt = datetime.fromisoformat(end_time) if end_time else now
    begin_dt = datetime.fromisoformat(begin_time) if begin_time else (end_dt - timedelta(hours=hours))

    args = {"begin_time": begin_dt.isoformat(), "end_time": end_dt.isoformat()}
    async with audit_context(tool="get_ash_sample", args=args):
        repo = AshRepository()
        return await repo.get_ash_sample(begin_time=begin_dt, end_time=end_dt)


async def get_ash_sql_activity(
    sql_id: str,
    begin_time: str | None = None,
    end_time: str | None = None,
    hours: int = 4,
) -> list[dict]:
    """
    Return historical ASH activity for a specific SQL_ID.

    Useful for understanding when a SQL was active, session state,
    wait events, and which time windows it contributed to wait time.

    Sources: DBA_HIST_ACTIVE_SESS_HISTORY
    """
    now = _now_utc()
    end_dt = datetime.fromisoformat(end_time) if end_time else now
    begin_dt = datetime.fromisoformat(begin_time) if begin_time else (end_dt - timedelta(hours=hours))

    args = {
        "sql_id": sql_id,
        "begin_time": begin_dt.isoformat(),
        "end_time": end_dt.isoformat(),
    }
    async with audit_context(tool="get_ash_sql_activity", args=args):
        repo = AshRepository()
        return await repo.get_ash_sql_activity(
            sql_id=sql_id, begin_time=begin_dt, end_time=end_dt
        )
