"""MCP tools — object.py: 6 PL/SQL object and code analysis tools."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.object_repo import ObjectRepository
from oracle_mcp.security.audit import audit_context


async def get_object_source(
    name: str,
    obj_type: str = "PROCEDURE",
    owner: str | None = None,
) -> dict:
    """
    Return the complete source code and metadata for a PL/SQL object.

    Parameters
    ----------
    name : str
        Object name (case-insensitive in Oracle — will be uppercased).
    obj_type : str
        Object type: PROCEDURE | FUNCTION | PACKAGE | PACKAGE BODY |
                     TRIGGER | TYPE | TYPE BODY (default: PROCEDURE)
    owner : str | None
        Schema owner. If None, searches all accessible schemas.

    Returns
    -------
    dict with:
      - owner, object_name, object_type, status, last_ddl_time, created
      - source_lines: list of {line, text}
      - line_count: total lines

    Sources: DBA_OBJECTS, ALL_SOURCE
    """
    name = name.upper()
    obj_type = obj_type.upper()
    args = {"name": name, "obj_type": obj_type, "owner": owner}

    async with audit_context(tool="get_object_source", args=args):
        repo = ObjectRepository()
        info, lines = await repo.get_object_source(name=name, obj_type=obj_type, owner=owner)

        return {
            **(info or {}),
            "source_lines": lines,
            "line_count": len(lines),
        }


async def get_object_metadata(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
) -> dict | None:
    """
    Return metadata for a database object (table, procedure, index, etc.)
    including table statistics freshness (last_analyzed, stale_stats).

    Sources: DBA_OBJECTS, DBA_TAB_STATISTICS
    """
    if name:
        name = name.upper()
    args = {"name": name, "obj_type": obj_type, "owner": owner}

    async with audit_context(tool="get_object_metadata", args=args):
        repo = ObjectRepository()
        return await repo.get_object_metadata(name=name, obj_type=obj_type, owner=owner)


async def get_object_arguments(
    name: str,
    owner: str | None = None,
) -> list[dict]:
    """
    Return the parameter list for a stored procedure or function.

    Parameters
    ----------
    name : str
        Procedure or function name.
    owner : str | None
        Schema owner.

    Sources: ALL_ARGUMENTS
    """
    args = {"name": name.upper(), "owner": owner}
    async with audit_context(tool="get_object_arguments", args=args):
        repo = ObjectRepository()
        return await repo.get_object_arguments(name=name.upper(), owner=owner)


async def get_object_dependencies(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
) -> list[dict]:
    """
    Return the direct dependencies of a database object
    (which tables, procedures, packages it references).

    Sources: ALL_DEPENDENCIES
    """
    args = {"name": name.upper(), "obj_type": obj_type, "owner": owner}
    async with audit_context(tool="get_object_dependencies", args=args):
        repo = ObjectRepository()
        return await repo.get_object_dependencies(
            name=name.upper(), obj_type=obj_type, owner=owner
        )


async def get_dependency_graph(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
    max_depth: int = 3,
) -> list[dict]:
    """
    Return the recursive dependency graph for a database object (up to max_depth levels).

    Each row shows a dependency edge: name → referenced_name with depth level.

    Parameters
    ----------
    max_depth : int
        Maximum recursion depth (default 3, max recommended: 5).

    Sources: ALL_DEPENDENCIES (recursive CTE)
    """
    max_depth = min(max_depth, 5)
    args = {"name": name.upper(), "obj_type": obj_type, "owner": owner, "max_depth": max_depth}
    async with audit_context(tool="get_dependency_graph", args=args):
        repo = ObjectRepository()
        return await repo.get_dependency_graph(
            name=name.upper(), obj_type=obj_type, owner=owner, max_depth=max_depth
        )


async def get_invalid_objects() -> list[dict]:
    """
    Return all INVALID objects in the database.

    Includes: PROCEDURE, FUNCTION, PACKAGE, PACKAGE BODY, TRIGGER,
              VIEW, SYNONYM, TYPE, TYPE BODY.

    Sources: DBA_OBJECTS
    """
    args: dict = {}
    async with audit_context(tool="get_invalid_objects", args=args):
        repo = ObjectRepository()
        return await repo.get_invalid_objects()
