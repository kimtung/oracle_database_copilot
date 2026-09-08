"""
oracle-mcp-server — MCP server entry point.

Registers all Oracle observability tools and starts the MCP server.
Transport is controlled by the MCP_TRANSPORT env var:
  - stdio (default) — for local AI clients (Claude Desktop, Cursor, etc.)
  - sse             — for remote HTTP clients

Usage
-----
    python -m oracle_mcp.server

or via the installed script:
    oracle-mcp-server
"""

from __future__ import annotations

import asyncio
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from oracle_mcp.config.settings import settings
from oracle_mcp.oracle.connection import close_pool
from oracle_mcp.tools import session as session_tools
from oracle_mcp.tools import sql as sql_tools
from oracle_mcp.tools import storage as storage_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ── Tool registry ─────────────────────────────────────────────────────────────

_TOOLS: list[Tool] = [
    # ── Storage / DB Info ──────────────────────────────────────────────────
    Tool(
        name="get_database_info",
        description=(
            "Return basic Oracle database and instance information: "
            "db name, version, instance name, host, startup time, log mode."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # ── SQL ───────────────────────────────────────────────────────────────
    Tool(
        name="get_top_sql",
        description=(
            "Return the top SQL statements ranked by a performance metric. "
            "Useful for identifying the heaviest queries in a time window."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "enum": ["elapsed_time", "cpu", "io", "buffer_gets", "executions"],
                    "description": "Ranking dimension (default: elapsed_time)",
                    "default": "elapsed_time",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum rows to return (default: 20, max: 100)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
                "hours": {
                    "type": "integer",
                    "description": "Look-back window in hours (default: 1)",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 168,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_sql_statistics",
        description=(
            "Return cumulative execution statistics for a specific SQL_ID. "
            "Includes executions, elapsed time, CPU, buffer gets, disk reads, "
            "rows processed, plan hash, and module/action context."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sql_id": {
                    "type": "string",
                    "description": "Oracle SQL identifier (up to 13 characters)",
                    "maxLength": 13,
                },
            },
            "required": ["sql_id"],
        },
    ),
    # ── Sessions ──────────────────────────────────────────────────────────
    Tool(
        name="get_active_sessions",
        description=(
            "Return all active USER sessions. "
            "Filter by minimum elapsed time to focus on long-running sessions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "min_elapsed_sec": {
                    "type": "integer",
                    "description": "Minimum LAST_CALL_ET in seconds (default: 0 → all active)",
                    "default": 0,
                    "minimum": 0,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_blocking_sessions",
        description=(
            "Detect and return all blocking session chains. "
            "Returns blocker→blocked tree with wait times. "
            "Returns empty list when no blocking exists."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="get_long_running_sessions",
        description=(
            "Return active sessions whose elapsed time exceeds a threshold. "
            "Useful for detecting runaway queries or stalled processes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "min_minutes": {
                    "type": "integer",
                    "description": "Minimum elapsed time in minutes (default: 60)",
                    "default": 60,
                    "minimum": 1,
                },
            },
            "required": [],
        },
    ),
]

# ── Dispatcher ────────────────────────────────────────────────────────────────

_DISPATCH = {
    "get_database_info":       storage_tools.get_database_info,
    "get_top_sql":             sql_tools.get_top_sql,
    "get_sql_statistics":      sql_tools.get_sql_statistics,
    "get_active_sessions":     session_tools.get_active_sessions,
    "get_blocking_sessions":   session_tools.get_blocking_sessions,
    "get_long_running_sessions": session_tools.get_long_running_sessions,
}

# ── MCP Server ────────────────────────────────────────────────────────────────

app = Server("oracle-mcp-server")


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return _TOOLS


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = _DISPATCH.get(name)
    if handler is None:
        raise ValueError(f"Unknown tool: {name!r}")

    result = await handler(**arguments)

    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


# ── Entry point ───────────────────────────────────────────────────────────────

async def _run_stdio() -> None:
    logger.info("Starting oracle-mcp-server (stdio transport) …")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main() -> None:
    transport = settings.mcp_transport.lower()

    if transport == "stdio":
        try:
            asyncio.run(_run_stdio())
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.run(close_pool())
    else:
        raise NotImplementedError(f"Transport '{transport}' not yet implemented. Use 'stdio'.")


if __name__ == "__main__":
    main()
