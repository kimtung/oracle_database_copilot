"""Audit logging for every MCP tool call.

Usage
-----
    async with audit_context(tool="get_top_sql", args={"metric": "elapsed_time"}):
        # ... run the tool ...

The context manager guarantees a log entry is written whether the tool
succeeds or raises an exception.  Logs go to *stderr* so they don't
interfere with the MCP stdio protocol on stdout.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from oracle_mcp.security.sanitizer import sanitize_args

logger = logging.getLogger(__name__)


@asynccontextmanager
async def audit_context(*, tool: str, args: dict[str, Any]):
    """
    Async context manager that wraps one MCP tool call and emits an audit
    record to stderr (JSON, one line) before yielding control back to the
    caller (after the tool has finished or raised).

    The record is ALWAYS written — success or error.
    """
    started_at = time.monotonic()
    utc_now = datetime.now(timezone.utc).isoformat()

    status = "success"
    error_msg: str | None = None

    try:
        yield  # ← tool runs here
    except Exception as exc:
        status = "error"
        error_msg = str(exc)
        raise
    finally:
        duration_ms = int((time.monotonic() - started_at) * 1000)
        _write(
            timestamp=utc_now,
            tool=tool,
            args=sanitize_args(args),
            duration_ms=duration_ms,
            status=status,
            error=error_msg,
        )


# ── Internal helpers ────────────────────────────────────────────────────────


def _write(
    *,
    timestamp: str,
    tool: str,
    args: dict,
    duration_ms: int,
    status: str,
    error: str | None,
) -> None:
    record: dict[str, Any] = {
        "timestamp": timestamp,
        "tool": tool,
        "args": args,
        "duration_ms": duration_ms,
        "status": status,
    }
    if error:
        record["error"] = error

    line = json.dumps(record, ensure_ascii=False)
    print(line, file=sys.stderr, flush=True)
