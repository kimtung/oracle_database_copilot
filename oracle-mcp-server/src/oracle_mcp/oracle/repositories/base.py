"""Base repository — thin async wrapper around python-oracledb."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import oracledb

from oracle_mcp.oracle.connection import get_pool


class BaseRepository:
    """Provides `_execute` helpers; subclasses hold the query strings."""

    @asynccontextmanager
    async def _connection(self):
        pool = await get_pool()
        conn: oracledb.AsyncConnection = await pool.acquire()
        try:
            yield conn
        finally:
            await pool.release(conn)

    async def _fetchall(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        """Execute *sql* and return all rows as list-of-dicts."""
        async with self._connection() as conn:
            cursor: oracledb.AsyncCursor = conn.cursor()
            await cursor.execute(sql, params or {})
            columns = [col[0].lower() for col in cursor.description]
            rows = await cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    async def _fetchone(self, sql: str, params: dict[str, Any] | None = None) -> dict | None:
        """Execute *sql* and return the first row as dict, or None."""
        async with self._connection() as conn:
            cursor: oracledb.AsyncCursor = conn.cursor()
            await cursor.execute(sql, params or {})
            columns = [col[0].lower() for col in cursor.description]
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(zip(columns, row))
