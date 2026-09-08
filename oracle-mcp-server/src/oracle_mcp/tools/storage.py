"""MCP tools — storage.py: get_database_info."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.security.audit import audit_context


async def get_database_info() -> dict:
    """
    Return basic Oracle database and instance information.

    Sources: V$DATABASE, V$INSTANCE
    """
    args: dict = {}
    async with audit_context(tool="get_database_info", args=args):
        repo = SqlRepository()
        info = await repo.get_database_info()
        return info.model_dump(mode="json")
