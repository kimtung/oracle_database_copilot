"""SourceCodeMapper — locates PL/SQL source code for a given sql_id.

Maps a SQL ID to its containing PL/SQL object (procedure/package/trigger)
by querying ASH data via MCP, then retrieves the relevant source fragment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from db_copilot.mcp.client import OracleMcpClient

logger = logging.getLogger(__name__)

_MAX_FRAGMENT_LINES = 40  # maximum source lines sent to LLM


@dataclass
class SourceFragment:
    object_name: str
    object_type: str
    owner: str
    start_line: int
    end_line: int
    source: str


class SourceCodeMapper:
    """Resolve sql_id -> PL/SQL source fragment via MCP tools.

    Only retrieves a limited fragment (±20 lines around the matching line)
    to avoid sending thousands of lines of PL/SQL to the LLM.
    """

    def __init__(self, mcp_client: OracleMcpClient) -> None:
        self._client = mcp_client

    async def map_sql_to_source(self, sql_id: str) -> SourceFragment | None:
        """Return a source fragment for the given sql_id, or None if unavailable."""
        # Step 1: find the PL/SQL object that contains this SQL via ASH
        plsql_info = await self._get_plsql_info(sql_id)
        if not plsql_info:
            return None

        object_name = plsql_info.get("plsql_entry_subprogram_id") or plsql_info.get(
            "module", ""
        )
        owner = plsql_info.get("parsing_schema_name", "")

        if not object_name:
            return None

        # Step 2: fetch source via get_object_source
        try:
            source_result = await self._client.call_tool(
                "get_object_source",
                {"object_name": object_name, "owner": owner or None},
            )
        except Exception as exc:
            logger.warning("Failed to retrieve source for %s: %s", object_name, exc)
            return None

        if not source_result or "source" not in source_result:
            return None

        full_source: str = source_result["source"]
        object_type: str = source_result.get("object_type", "PROCEDURE")

        # Step 3: find the SQL text fragment within the source (heuristic)
        fragment, start_line, end_line = self._extract_fragment(full_source)

        return SourceFragment(
            object_name=object_name,
            object_type=object_type,
            owner=owner,
            start_line=start_line,
            end_line=end_line,
            source=fragment,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _get_plsql_info(self, sql_id: str) -> dict | None:
        """Query ASH to find the PL/SQL context for this sql_id."""
        try:
            result = await self._client.call_tool(
                "get_ash_sql_activity",
                {"sql_id": sql_id, "minutes": 60},
            )
            if isinstance(result, list) and result:
                return result[0]
            if isinstance(result, dict):
                return result
        except Exception as exc:
            logger.warning("ASH lookup for sql_id=%s failed: %s", sql_id, exc)
        return None

    @staticmethod
    def _extract_fragment(source: str) -> tuple[str, int, int]:
        """Extract a limited fragment from the full source.

        Returns (fragment_text, start_line_number, end_line_number).
        """
        lines = source.splitlines()
        total = len(lines)
        if total <= _MAX_FRAGMENT_LINES:
            return source, 1, total

        # Heuristic: look for SELECT/INSERT/UPDATE/DELETE/MERGE keywords
        target_line = 1
        for i, line in enumerate(lines, start=1):
            uline = line.upper().strip()
            if any(kw in uline for kw in ("SELECT", "UPDATE", "DELETE", "INSERT", "MERGE")):
                target_line = i
                break

        half = _MAX_FRAGMENT_LINES // 2
        start_line = max(1, target_line - half)
        end_line = min(total, start_line + _MAX_FRAGMENT_LINES - 1)
        fragment = "\n".join(lines[start_line - 1 : end_line])
        return fragment, start_line, end_line
