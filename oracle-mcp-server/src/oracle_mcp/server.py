"""
oracle-mcp-server — MCP server entry point (MCP SDK 2.x).

Uses MCPServer with @mcp.tool() decorator pattern.

32 tools across 7 groups:
  SQL (4)      get_top_sql, get_sql_statistics, get_sql_wait_events, get_sql_execution_context
  ASH (2)      get_ash_sample, get_ash_sql_activity
  AWR (2)      get_awr_snapshot, get_awr_sql_stats
  Session (5)  get_active_sessions, get_session, get_session_waits,
               get_blocking_sessions, get_long_running_sessions
  Plan (2)     get_sql_plan, get_sql_plan_history
  Object (6)   get_object_source, get_object_metadata, get_object_arguments,
               get_object_dependencies, get_dependency_graph, get_invalid_objects
  Storage (11) get_database_info, get_tablespace_usage, get_datafile_usage,
               get_segment_growth, get_temp_usage, get_undo_usage,
               get_redo_statistics, get_resource_usage,
               get_scheduler_jobs, get_scheduler_job_history, get_failed_jobs
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from mcp.server.mcpserver import MCPServer

from oracle_mcp.tools import ash as _ash
from oracle_mcp.tools import awr as _awr
from oracle_mcp.tools import object as _obj
from oracle_mcp.tools import plan as _plan
from oracle_mcp.tools import session as _session
from oracle_mcp.tools import sql as _sql
from oracle_mcp.tools import storage as _storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    stream=sys.stderr,
)

mcp = MCPServer("oracle-mcp-server")

# ── SQL Tools ─────────────────────────────────────────────────────────────────

@mcp.tool(description="Return top SQL ranked by elapsed_time|cpu|io|buffer_gets|executions (V$SQLSTATS).")
async def get_top_sql(metric: str = "elapsed_time", limit: int = 20, hours: int = 1) -> Any:
    return await _sql.get_top_sql(metric=metric, limit=limit, hours=hours)


@mcp.tool(description="Return cumulative execution statistics for a SQL_ID (V$SQL).")
async def get_sql_statistics(sql_id: str) -> Any:
    return await _sql.get_sql_statistics(sql_id=sql_id)


@mcp.tool(description="Return aggregated wait events for a SQL_ID (V$ACTIVE_SESSION_HISTORY).")
async def get_sql_wait_events(sql_id: str, hours: int = 4) -> Any:
    return await _sql.get_sql_wait_events(sql_id=sql_id, hours=hours)


@mcp.tool(description="Return module/action/program calling context for a SQL_ID (V$ASH).")
async def get_sql_execution_context(sql_id: str, hours: int = 4) -> Any:
    return await _sql.get_sql_execution_context(sql_id=sql_id, hours=hours)


# ── ASH Tools ─────────────────────────────────────────────────────────────────

@mcp.tool(description="Return ASH samples from V$ACTIVE_SESSION_HISTORY for a time range.")
async def get_ash_sample(
    begin_time: str | None = None,
    end_time: str | None = None,
    hours: int = 1,
) -> Any:
    return await _ash.get_ash_sample(begin_time=begin_time, end_time=end_time, hours=hours)


@mcp.tool(description="Return historical ASH activity for a SQL_ID (DBA_HIST_ACTIVE_SESS_HISTORY).")
async def get_ash_sql_activity(
    sql_id: str,
    begin_time: str | None = None,
    end_time: str | None = None,
    hours: int = 4,
) -> Any:
    return await _ash.get_ash_sql_activity(
        sql_id=sql_id, begin_time=begin_time, end_time=end_time, hours=hours
    )


# ── AWR Tools ─────────────────────────────────────────────────────────────────

@mcp.tool(description="Return AWR snapshot intervals (DBA_HIST_SNAPSHOT).")
async def get_awr_snapshot(hours: int = 24) -> Any:
    return await _awr.get_awr_snapshot(hours=hours)


@mcp.tool(description="Return per-snapshot AWR stats for a SQL_ID (DBA_HIST_SQLSTAT).")
async def get_awr_sql_stats(
    sql_id: str,
    days: int = 1,
    begin_snap: int | None = None,
    end_snap: int | None = None,
) -> Any:
    return await _awr.get_awr_sql_stats(
        sql_id=sql_id, days=days, begin_snap=begin_snap, end_snap=end_snap
    )


# ── Session Tools ─────────────────────────────────────────────────────────────

@mcp.tool(description="Return all active USER sessions (V$SESSION).")
async def get_active_sessions(min_elapsed_sec: int = 0) -> Any:
    return await _session.get_active_sessions(min_elapsed_sec=min_elapsed_sec)


@mcp.tool(description="Return detailed info for a specific session by SID + SERIAL#.")
async def get_session(sid: int, serial: int) -> Any:
    return await _session.get_session(sid=sid, serial=serial)


@mcp.tool(description="Return current wait event details for a session (V$SESSION_WAIT).")
async def get_session_waits(sid: int) -> Any:
    return await _session.get_session_waits(sid=sid)


@mcp.tool(description="Return blocking session chains with blocker→blocked tree (V$SESSION).")
async def get_blocking_sessions() -> Any:
    return await _session.get_blocking_sessions()


@mcp.tool(description="Return sessions running longer than min_minutes (V$SESSION).")
async def get_long_running_sessions(min_minutes: int = 60) -> Any:
    return await _session.get_long_running_sessions(min_minutes=min_minutes)


# ── Plan Tools ────────────────────────────────────────────────────────────────

@mcp.tool(description="Return the current execution plan for a SQL_ID (V$SQL_PLAN).")
async def get_sql_plan(sql_id: str) -> Any:
    return await _plan.get_sql_plan(sql_id=sql_id)


@mcp.tool(description="Return distinct execution plans seen in AWR — detects plan regressions.")
async def get_sql_plan_history(sql_id: str, days: int = 7) -> Any:
    return await _plan.get_sql_plan_history(sql_id=sql_id, days=days)


# ── Object / Code Tools ───────────────────────────────────────────────────────

@mcp.tool(description="Return full PL/SQL source code + metadata for a stored object.")
async def get_object_source(
    name: str,
    obj_type: str = "PROCEDURE",
    owner: str | None = None,
) -> Any:
    return await _obj.get_object_source(name=name, obj_type=obj_type, owner=owner)


@mcp.tool(description="Return object metadata including table statistics freshness (stale_stats, last_analyzed).")
async def get_object_metadata(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
) -> Any:
    return await _obj.get_object_metadata(name=name, obj_type=obj_type, owner=owner)


@mcp.tool(description="Return parameter list for a stored procedure or function (ALL_ARGUMENTS).")
async def get_object_arguments(name: str, owner: str | None = None) -> Any:
    return await _obj.get_object_arguments(name=name, owner=owner)


@mcp.tool(description="Return direct dependencies of a database object (ALL_DEPENDENCIES).")
async def get_object_dependencies(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
) -> Any:
    return await _obj.get_object_dependencies(name=name, obj_type=obj_type, owner=owner)


@mcp.tool(description="Return recursive dependency graph up to max_depth levels (ALL_DEPENDENCIES CTE).")
async def get_dependency_graph(
    name: str,
    obj_type: str | None = None,
    owner: str | None = None,
    max_depth: int = 3,
) -> Any:
    return await _obj.get_dependency_graph(
        name=name, obj_type=obj_type, owner=owner, max_depth=max_depth
    )


@mcp.tool(description="Return all INVALID PL/SQL objects in the database (DBA_OBJECTS).")
async def get_invalid_objects() -> Any:
    return await _obj.get_invalid_objects()


# ── Storage / Health Tools ────────────────────────────────────────────────────

@mcp.tool(description="Return Oracle DB/instance info: name, version, host, startup time (V$DATABASE, V$INSTANCE).")
async def get_database_info() -> Any:
    return await _storage.get_database_info()


@mcp.tool(description="Return used%, used bytes, free bytes for all tablespaces.")
async def get_tablespace_usage() -> Any:
    return await _storage.get_tablespace_usage()


@mcp.tool(description="Return individual datafile details for a specific tablespace (DBA_DATA_FILES).")
async def get_datafile_usage(tablespace_name: str) -> Any:
    return await _storage.get_datafile_usage(tablespace_name=tablespace_name)


@mcp.tool(description="Return current segment size for a table/index/LOB (DBA_SEGMENTS).")
async def get_segment_growth(
    name: str,
    owner: str | None = None,
    segment_type: str | None = None,
) -> Any:
    return await _storage.get_segment_growth(name=name, owner=owner, segment_type=segment_type)


@mcp.tool(description="Return TEMP tablespace current usage (DBA_TEMP_FILES, V$TEMPSTAT).")
async def get_temp_usage() -> Any:
    return await _storage.get_temp_usage()


@mcp.tool(description="Return recent UNDO statistics: active/unexpired/expired blocks (V$UNDOSTAT).")
async def get_undo_usage() -> Any:
    return await _storage.get_undo_usage()


@mcp.tool(description="Return redo log status and archived log generation rate (V$LOG, V$ARCHIVED_LOG).")
async def get_redo_statistics(hours: int = 24) -> Any:
    return await _storage.get_redo_statistics(hours=hours)


@mcp.tool(description="Return key system statistics: reads, writes, commits, parses (V$SYSSTAT).")
async def get_resource_usage() -> Any:
    return await _storage.get_resource_usage()


@mcp.tool(description="Return all Oracle Scheduler jobs with state and run counts (DBA_SCHEDULER_JOBS).")
async def get_scheduler_jobs() -> Any:
    return await _storage.get_scheduler_jobs()


@mcp.tool(description="Return execution history for a specific scheduler job (DBA_SCHEDULER_JOB_RUN_DETAILS).")
async def get_scheduler_job_history(
    job_name: str,
    owner: str | None = None,
    days: int = 7,
) -> Any:
    return await _storage.get_scheduler_job_history(job_name=job_name, owner=owner, days=days)


@mcp.tool(description="Return all scheduler jobs that failed (status != SUCCEEDED) in the last N hours.")
async def get_failed_jobs(hours: int = 24) -> Any:
    return await _storage.get_failed_jobs(hours=hours)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
