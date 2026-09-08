"""Pydantic response models — oracle_mcp output contracts.

All MCP tools return instances of these models (serialised via .model_dump()).
Pydantic validates the data coming out of Oracle so callers get a consistent,
predictable shape regardless of driver quirks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ── Shared helpers ───────────────────────────────────────────────────────────

class _Base(BaseModel):
    """Common config for all response models."""

    model_config = {"populate_by_name": True}


# ── Database / Instance ──────────────────────────────────────────────────────

class DatabaseInfo(_Base):
    db_name: str
    db_unique_name: str | None = None
    instance_name: str
    host_name: str
    version: str
    status: str
    log_mode: str | None = None
    logins: str | None = None
    startup_time: datetime | None = None
    created: datetime | None = None


# ── SQL ──────────────────────────────────────────────────────────────────────

class SqlSummary(_Base):
    sql_id: str
    sql_text_fragment: str | None = None
    executions: int = 0
    elapsed_time_sec: float = 0.0
    cpu_time_sec: float = 0.0
    buffer_gets: int = 0
    disk_reads: int = 0
    rows_processed: int = 0
    plan_hash_value: int | None = None
    module: str | None = None
    action: str | None = None
    last_active_time: datetime | None = None

    @field_validator("sql_id")
    @classmethod
    def validate_sql_id(cls, v: str) -> str:
        if len(v) > 13:
            raise ValueError(f"sql_id must be ≤13 chars, got {len(v)}")
        return v


class SqlStatistics(SqlSummary):
    """Extended statistics for a single SQL_ID."""

    sql_text: str | None = None
    avg_elapsed_sec: float = 0.0
    avg_cpu_sec: float = 0.0
    avg_buffer_gets: float = 0.0
    avg_disk_reads: float = 0.0


# ── Sessions ─────────────────────────────────────────────────────────────────

class Session(_Base):
    sid: int
    serial: int = Field(alias="serial#", default=0)
    username: str | None = None
    status: str
    sql_id: str | None = None
    prev_sql_id: str | None = None
    module: str | None = None
    action: str | None = None
    machine: str | None = None
    program: str | None = None
    osuser: str | None = None
    logon_time: datetime | None = None
    elapsed_seconds: int = 0
    blocking_session: int | None = None
    blocking_session_status: str | None = None
    wait_event: str | None = None
    wait_time: int = 0
    seconds_in_wait: int = 0


class BlockedSession(_Base):
    blocked_sid: int
    blocked_serial: int = Field(alias="blocked_serial#", default=0)
    blocked_user: str | None = None
    blocked_sql_id: str | None = None
    blocked_wait_event: str | None = None
    blocked_wait_sec: int = 0


class BlockingChain(_Base):
    blocker_sid: int
    blocker_serial: int = Field(alias="blocker_serial#", default=0)
    blocker_user: str | None = None
    blocker_sql_id: str | None = None
    blocker_wait_event: str | None = None
    blocker_elapsed_sec: int = 0
    blocked_sessions: list[BlockedSession] = Field(default_factory=list)


class BlockingResult(_Base):
    blocking_chains: list[BlockingChain]
    total_blocked: int
    max_wait_seconds: int


class LongRunningSession(_Base):
    sid: int
    serial: int = Field(alias="serial#", default=0)
    username: str | None = None
    sql_id: str | None = None
    module: str | None = None
    action: str | None = None
    machine: str | None = None
    logon_time: datetime | None = None
    elapsed_seconds: int = 0
    wait_event: str | None = None
    state: str | None = None
