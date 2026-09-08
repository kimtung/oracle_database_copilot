"""MCP tools — plan.py: get_sql_plan, get_sql_plan_history."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.object_repo import ObjectRepository
from oracle_mcp.security.audit import audit_context


async def get_sql_plan(sql_id: str) -> list[dict]:
    """
    Return the current execution plan for a SQL_ID.

    Returns each plan line with: operation, options, object_name,
    cardinality (estimated rows), cost, access predicates, filter predicates.

    Sources: V$SQL_PLAN
    """
    args = {"sql_id": sql_id}
    async with audit_context(tool="get_sql_plan", args=args):
        repo = ObjectRepository()
        return await repo.get_sql_plan(sql_id=sql_id)


async def get_sql_plan_history(sql_id: str, days: int = 7) -> list[dict]:
    """
    Return the history of distinct execution plans for a SQL_ID.

    Each entry shows a plan hash, when it was first/last seen in AWR,
    total executions, and average elapsed time under that plan.
    Useful for detecting plan regressions.

    Parameters
    ----------
    sql_id : str
        Oracle SQL identifier.
    days : int
        Look-back window in days (default 7).

    Sources: DBA_HIST_SQL_PLAN, DBA_HIST_SQLSTAT
    """
    args = {"sql_id": sql_id, "days": days}
    async with audit_context(tool="get_sql_plan_history", args=args):
        repo = ObjectRepository()
        return await repo.get_sql_plan_history(sql_id=sql_id, days=days)
