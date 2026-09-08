"""MCP tools — session.py: get_active_sessions, get_blocking_sessions, get_long_running_sessions."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.security.audit import audit_context


async def get_active_sessions(min_elapsed_sec: int = 0) -> list[dict]:
    """
    Return all active USER sessions with elapsed time >= *min_elapsed_sec*.

    Parameters
    ----------
    min_elapsed_sec : int
        Minimum LAST_CALL_ET threshold in seconds (default 0 → all active).

    Sources: V$SESSION (type='USER', status != 'INACTIVE')
    """
    args = {"min_elapsed_sec": min_elapsed_sec}
    async with audit_context(tool="get_active_sessions", args=args):
        repo = SqlRepository()
        results = await repo.get_active_sessions(min_elapsed_sec=min_elapsed_sec)
        return [r.model_dump(mode="json") for r in results]


async def get_blocking_sessions() -> dict:
    """
    Detect blocking session chains and return the full blocker→blocked tree.

    Returns a summary with:
    - ``blocking_chains``: list of blocker sessions, each with their blocked sessions
    - ``total_blocked``: total number of sessions being blocked
    - ``max_wait_seconds``: longest current wait in the blocking chains

    Sources: V$SESSION (self-join on BLOCKING_SESSION)
    """
    args: dict = {}
    async with audit_context(tool="get_blocking_sessions", args=args):
        repo = SqlRepository()
        result = await repo.get_blocking_sessions()
        return result.model_dump(mode="json")


async def get_long_running_sessions(min_minutes: int = 60) -> list[dict]:
    """
    Return active sessions whose elapsed time exceeds *min_minutes*.

    Parameters
    ----------
    min_minutes : int
        Minimum elapsed time in minutes (default 60).

    Sources: V$SESSION (ACTIVE status, LAST_CALL_ET >= threshold)
    """
    args = {"min_minutes": min_minutes}
    async with audit_context(tool="get_long_running_sessions", args=args):
        repo = SqlRepository()
        results = await repo.get_long_running_sessions(min_minutes=min_minutes)
        return [r.model_dump(mode="json") for r in results]
