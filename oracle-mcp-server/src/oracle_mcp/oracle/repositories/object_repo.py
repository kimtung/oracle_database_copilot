"""Repository for execution plans and PL/SQL objects."""

from __future__ import annotations

from oracle_mcp.oracle.queries import object_queries as Q
from oracle_mcp.oracle.repositories.base import BaseRepository


class ObjectRepository(BaseRepository):

    # ── Execution Plans ───────────────────────────────────────────────────

    async def get_sql_plan(self, sql_id: str) -> list[dict]:
        """Return execution plan rows from V$SQL_PLAN."""
        return await self._fetchall(Q.SQL_PLAN_CURRENT, {"sql_id": sql_id})

    async def get_sql_plan_history(self, sql_id: str, days: int = 7) -> list[dict]:
        """Return distinct plan hashes seen in AWR over past N days."""
        return await self._fetchall(
            Q.SQL_PLAN_HISTORY,
            {"sql_id": sql_id, "days": days},
        )

    # ── Objects ───────────────────────────────────────────────────────────

    async def get_object_metadata(
        self, name: str, obj_type: str | None, owner: str | None
    ) -> dict | None:
        return await self._fetchone(
            Q.OBJECT_METADATA,
            {"name": name, "obj_type": obj_type, "owner": owner},
        )

    async def get_object_source(
        self, name: str, obj_type: str, owner: str | None
    ) -> tuple[dict | None, list[dict]]:
        """Return (object_info, source_lines)."""
        info = await self._fetchone(
            Q.OBJECT_SOURCE,
            {"name": name, "obj_type": obj_type, "owner": owner},
        )
        lines = await self._fetchall(
            Q.OBJECT_SOURCE_LINES,
            {"name": name, "obj_type": obj_type, "owner": owner},
        )
        return info, lines

    async def get_object_arguments(
        self, name: str, owner: str | None
    ) -> list[dict]:
        return await self._fetchall(
            Q.OBJECT_ARGUMENTS,
            {"name": name, "owner": owner},
        )

    async def get_object_dependencies(
        self, name: str, obj_type: str | None, owner: str | None
    ) -> list[dict]:
        return await self._fetchall(
            Q.OBJECT_DEPENDENCIES,
            {"name": name, "obj_type": obj_type, "owner": owner},
        )

    async def get_dependency_graph(
        self, name: str, obj_type: str | None, owner: str | None, max_depth: int = 3
    ) -> list[dict]:
        return await self._fetchall(
            Q.DEPENDENCY_GRAPH,
            {"name": name, "obj_type": obj_type, "owner": owner, "max_depth": max_depth},
        )

    async def get_invalid_objects(self) -> list[dict]:
        return await self._fetchall(Q.INVALID_OBJECTS)
