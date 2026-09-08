# Oracle MCP Server Design
# Thiết Kế Oracle MCP Server

**Project:** `oracle-mcp-server`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

`oracle-mcp-server` là một **project độc lập** đóng vai trò **Oracle Observability & Evidence Gateway**.

Nó implement **Model Context Protocol (MCP)** để cung cấp các Oracle read-only tools cho AI agents hoặc bất kỳ MCP client nào (bao gồm `db-copilot`).

### 1.1 Nguyên tắc thiết kế

| Nguyên tắc | Giải thích |
|---|---|
| **Semantic tools, không phải generic SQL** | Mỗi tool có ngữ nghĩa rõ ràng, không có `execute_sql()` |
| **Read-only tuyệt đối** | Oracle account chỉ có SELECT privileges |
| **Structured output** | Mọi tool trả về Pydantic model, không phải raw rows |
| **Audit mọi call** | Mọi tool call đều được log với timestamp, args, duration |
| **Stateless** | Không có database riêng, không lưu state |
| **Fail-safe** | Lỗi query → trả về error có cấu trúc, không crash server |

---

## 2. MCP Protocol

### 2.1 Transport Modes

| Mode | Cách dùng |
|---|---|
| **Stdio** | `db-copilot` spawn `oracle-mcp-server` process, giao tiếp qua stdin/stdout |
| **SSE** | `oracle-mcp-server` chạy như HTTP server, client kết nối qua Server-Sent Events |

**MVP:** Stdio mode (đơn giản hơn, không cần network config)

### 2.2 MCP Server Entry Point

```python
# src/oracle_mcp/server.py

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from oracle_mcp.tools import sql, ash, awr, session, plan, object_, storage
from oracle_mcp.config.settings import Settings

settings = Settings()
app = Server("oracle-mcp-server")

# Register all tools
for tool_fn in [
    *sql.get_tools(),
    *ash.get_tools(),
    *awr.get_tools(),
    *session.get_tools(),
    *plan.get_tools(),
    *object_.get_tools(),
    *storage.get_tools(),
]:
    app.add_tool(tool_fn)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Tool Catalog Đầy Đủ

### Group 1: SQL Tools (`tools/sql.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_top_sql` | `metric, limit, hours` | `V$SQL`, `V$SQLSTATS` | `List[SqlSummary]` |
| `get_sql_statistics` | `sql_id` | `V$SQL`, `DBA_HIST_SQLSTAT` | `SqlStatistics` |
| `get_sql_wait_events` | `sql_id, hours` | `V$SESSION_WAIT`, `ASH` | `List[WaitEvent]` |
| `get_sql_execution_context` | `sql_id` | `V$SQL.MODULE/ACTION` | `ExecutionContext` |

### Group 2: ASH Tools (`tools/ash.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_ash_sample` | `begin_time, end_time` | `V$ACTIVE_SESSION_HISTORY` | `List[AshSample]` |
| `get_ash_sql_activity` | `sql_id, begin_time, end_time` | `DBA_HIST_ACTIVE_SESS_HISTORY` | `AshActivity` |

### Group 3: AWR Tools (`tools/awr.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_awr_snapshot` | `hours` | `DBA_HIST_SNAPSHOT` | `List[AwrSnapshot]` |
| `get_awr_sql_stats` | `sql_id, begin_snap, end_snap` | `DBA_HIST_SQLSTAT` | `AwrSqlStats` |

### Group 4: Session Tools (`tools/session.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_active_sessions` | `min_elapsed_sec` | `V$SESSION` | `List[Session]` |
| `get_session` | `session_id, serial` | `V$SESSION` | `SessionDetail` |
| `get_session_waits` | `session_id` | `V$SESSION_WAIT` | `List[SessionWait]` |
| `get_blocking_sessions` | — | `V$SESSION` (self-join) | `List[BlockingChain]` |
| `get_long_running_sessions` | `min_minutes` | `V$SESSION.LAST_CALL_ET` | `List[Session]` |

### Group 5: Plan Tools (`tools/plan.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_sql_plan` | `sql_id` | `V$SQL_PLAN` | `ExecutionPlan` |
| `get_sql_plan_history` | `sql_id, days` | `DBA_HIST_SQL_PLAN`, `DBA_HIST_SQLSTAT` | `List[PlanHistory]` |

### Group 6: Object/Code Tools (`tools/object.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_object_source` | `owner, name, type` | `ALL_SOURCE` | `ObjectSource` |
| `get_object_metadata` | `owner, name, type` | `DBA_OBJECTS`, `DBA_TAB_STATISTICS` | `ObjectMetadata` |
| `get_object_arguments` | `owner, name` | `ALL_ARGUMENTS` | `List[Argument]` |
| `get_object_dependencies` | `owner, name, type` | `ALL_DEPENDENCIES` | `List[Dependency]` |
| `get_dependency_graph` | `owner, name, type, depth` | `ALL_DEPENDENCIES` (recursive) | `DependencyGraph` |
| `get_invalid_objects` | — | `DBA_OBJECTS` | `List[InvalidObject]` |

### Group 7: Storage Tools (`tools/storage.py`)

| Tool | Input | Oracle Source | Output |
|---|---|---|---|
| `get_tablespace_usage` | — | `DBA_DATA_FILES`, `DBA_FREE_SPACE` | `List[TablespaceUsage]` |
| `get_datafile_usage` | `tablespace_name` | `DBA_DATA_FILES` | `List[DatafileUsage]` |
| `get_segment_growth` | `owner, name, days` | `DBA_SEGMENTS` | `SegmentGrowth` |
| `get_temp_usage` | — | `V$TEMPSTAT`, `DBA_TEMP_FILES` | `TempUsage` |
| `get_undo_usage` | — | `V$UNDOSTAT` | `UndoUsage` |
| `get_database_info` | — | `V$DATABASE`, `V$INSTANCE`, `V$PARAMETER` | `DatabaseInfo` |
| `get_resource_usage` | — | `V$SYSSTAT`, `V$SYSEVENT` | `ResourceUsage` |
| `get_redo_statistics` | `hours` | `V$LOG`, `V$ARCHIVED_LOG` | `RedoStatistics` |
| `get_alert_events` | `hours` | `V$DIAG_ALERT_EXT` | `List[AlertEvent]` |
| `get_scheduler_jobs` | — | `DBA_SCHEDULER_JOBS` | `List[JobStatus]` |
| `get_scheduler_job_history` | `job_name, days` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | `List[JobRun]` |
| `get_failed_jobs` | `hours` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | `List[JobRun]` |

---

## 4. Tool Implementation Pattern

```python
# src/oracle_mcp/tools/sql.py

from mcp.types import Tool
from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.security.audit import AuditContext
from oracle_mcp.models.sql_models import SqlStatistics

async def get_sql_statistics(sql_id: str) -> dict:
    """
    Lấy cumulative execution statistics cho một SQL_ID.
    Source: V$SQL (real-time) và DBA_HIST_SQLSTAT (historical).
    """
    async with AuditContext(tool="get_sql_statistics", args={"sql_id": sql_id}):
        repo = SqlRepository()
        stats: SqlStatistics = await repo.get_sql_statistics(sql_id)
        return stats.model_dump()

def get_tools() -> list[Tool]:
    return [
        Tool(
            name="get_sql_statistics",
            description=(
                "Get cumulative execution statistics for a specific SQL_ID. "
                "Includes executions, elapsed time, CPU time, buffer gets, "
                "disk reads, rows processed, and current plan hash."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_id": {
                        "type": "string",
                        "description": "Oracle SQL_ID (13-character identifier)"
                    }
                },
                "required": ["sql_id"]
            },
            fn=get_sql_statistics
        ),
        # ... other tools
    ]
```

---

## 5. Oracle Connection

```python
# src/oracle_mcp/oracle/connection.py

import oracledb
from oracle_mcp.config.settings import Settings

class OracleConnectionPool:
    """
    Singleton async connection pool.
    python-oracledb thin mode (không cần Oracle Client).
    """
    _pool: oracledb.AsyncConnectionPool | None = None

    @classmethod
    async def initialize(cls):
        s = Settings()
        cls._pool = await oracledb.create_pool_async(
            user=s.oracle_user,
            password=s.oracle_password,
            dsn=s.oracle_dsn,
            min=2,
            max=10,
            increment=1
        )

    @classmethod
    async def acquire(cls) -> oracledb.AsyncConnection:
        if cls._pool is None:
            await cls.initialize()
        return await cls._pool.acquire()
```

---

## 6. Audit System

```python
# src/oracle_mcp/security/audit.py

import time
import json
from contextlib import asynccontextmanager
from oracle_mcp.security.sanitizer import sanitize_args

@asynccontextmanager
async def AuditContext(tool: str, args: dict):
    """
    Context manager: log mọi MCP tool call.
    Ghi log TRƯỚC khi trả kết quả.
    """
    start = time.time()
    sanitized = sanitize_args(args)

    try:
        yield
        duration_ms = int((time.time() - start) * 1000)
        _write_audit_log(tool, sanitized, duration_ms, status="success")
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        _write_audit_log(tool, sanitized, duration_ms, status="error", error=str(e))
        raise

def _write_audit_log(tool, args, duration_ms, status, error=None):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool": tool,
        "args": args,
        "duration_ms": duration_ms,
        "status": status,
        "error": error
    }
    # Ghi ra stderr (stdout là MCP protocol) hoặc file
    print(json.dumps(record), file=sys.stderr)
```

---

## 7. Security: Oracle Permissions

```sql
-- Tạo read-only user
CREATE USER db_copilot_readonly IDENTIFIED BY "<password>";

-- AWR / ASH
GRANT SELECT ON SYS.DBA_HIST_SQLSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQL_PLAN TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SNAPSHOT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_SQLTEXT TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_HIST_ACTIVE_SESS_HISTORY TO db_copilot_readonly;

-- V$ Dynamic Views
GRANT SELECT ON SYS.V_$SQL TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQLSTATS TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SESSION_WAIT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SQL_PLAN_STATISTICS_ALL TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$ACTIVE_SESSION_HISTORY TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$UNDOSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$TEMPSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$DATABASE TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$INSTANCE TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$PARAMETER TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSSTAT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$SYSEVENT TO db_copilot_readonly;
GRANT SELECT ON SYS.V_$LOG TO db_copilot_readonly;

-- Storage
GRANT SELECT ON SYS.DBA_DATA_FILES TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_FREE_SPACE TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SEGMENTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TABLESPACES TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TEMP_FILES TO db_copilot_readonly;

-- Jobs
GRANT SELECT ON SYS.DBA_SCHEDULER_JOBS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_JOB_RUN_DETAILS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_SCHEDULER_RUNNING_JOBS TO db_copilot_readonly;

-- Code / Objects
GRANT SELECT ON SYS.ALL_SOURCE TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_OBJECTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_OBJECTS TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_DEPENDENCIES TO db_copilot_readonly;
GRANT SELECT ON SYS.ALL_ARGUMENTS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_TAB_STATISTICS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_IND_STATISTICS TO db_copilot_readonly;
GRANT SELECT ON SYS.DBA_INDEXES TO db_copilot_readonly;

-- Không cấp: DML, DDL, EXECUTE, DBA role
```

---

## 8. Tool Output Contracts

### get_sql_statistics

```json
{
  "sql_id": "8f3abc",
  "sql_text_fragment": "SELECT * FROM ACCOUNT_POSITION WHERE ...",
  "executions": 12450,
  "elapsed_time_ms": 52300000,
  "cpu_time_ms": 21300000,
  "buffer_gets": 182000000,
  "disk_reads": 9300000,
  "rows_processed": 4200000,
  "last_active_time": "2026-09-08T14:32:00Z",
  "plan_hash_value": 98237412,
  "module": "PROC_SETTLEMENT",
  "action": "UPDATE_PHASE"
}
```

### get_blocking_sessions

```json
{
  "blocking_chains": [
    {
      "blocker": {
        "session_id": 142, "serial": 1023,
        "user": "APP", "sql_id": "abc123",
        "wait_event": "enq: TX - row lock contention",
        "elapsed_seconds": 423
      },
      "blocked": [
        {"session_id": 156, "serial": 2011, "sql_id": "def456"}
      ]
    }
  ],
  "total_blocked": 1,
  "max_wait_seconds": 423
}
```

### get_object_source

```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE",
  "status": "VALID",
  "last_ddl_time": "2026-09-01T10:00:00Z",
  "source_hash": "sha256:abc123...",
  "source_lines": 312,
  "source": "CREATE OR REPLACE PROCEDURE PROC_SETTLEMENT ...",
  "sql_statements": [
    {"line": 247, "type": "UPDATE", "table": "ACCOUNT_POSITION"}
  ],
  "dependencies": [
    {"owner": "APP", "name": "ACCOUNT_POSITION", "type": "TABLE"},
    {"owner": "APP", "name": "PROC_CALCULATE", "type": "PROCEDURE"}
  ]
}
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

`oracle-mcp-server` is a **standalone project** acting as the **Oracle Observability & Evidence Gateway**.

It implements the **Model Context Protocol (MCP)** to expose Oracle read-only tools to AI agents or any MCP client (including `db-copilot`).

### 9.1 Design Principles

| Principle | Explanation |
|---|---|
| **Semantic tools, not generic SQL** | Each tool has clear semantics, no `execute_sql()` |
| **Absolutely read-only** | Oracle account has SELECT privileges only |
| **Structured output** | All tools return Pydantic models, not raw rows |
| **Audit every call** | Every tool call logged: timestamp, args, duration |
| **Stateless** | No own database, no stored state |
| **Fail-safe** | Query error → structured error response, no server crash |

---

## 10. Tool Groups Summary

- **sql.py** (4 tools): `get_top_sql`, `get_sql_statistics`, `get_sql_wait_events`, `get_sql_execution_context`
- **ash.py** (2 tools): `get_ash_sample`, `get_ash_sql_activity`
- **awr.py** (2 tools): `get_awr_snapshot`, `get_awr_sql_stats`
- **session.py** (5 tools): `get_active_sessions`, `get_session`, `get_session_waits`, `get_blocking_sessions`, `get_long_running_sessions`
- **plan.py** (2 tools): `get_sql_plan`, `get_sql_plan_history`
- **object.py** (6 tools): `get_object_source`, `get_object_metadata`, `get_object_arguments`, `get_object_dependencies`, `get_dependency_graph`, `get_invalid_objects`
- **storage.py** (11 tools): tablespace, temp, undo, segments, redo, jobs, db info, alerts, resources

**Total: ~32 tools**

---

## 11. Security

- Oracle credentials only in `oracle-mcp-server` — read from environment variables
- Never logged (sanitizer removes credentials from audit args)
- Never passed to `db-copilot` or LLM
- SELECT-only grants on ~35 pre-approved views/tables
- No DML, DDL, EXECUTE, or DBA role granted

---

## 12. Audit

Every MCP tool call is audit-logged to stderr (stdout is reserved for MCP protocol):

```json
{
  "timestamp": "2026-09-08T14:32:01Z",
  "tool": "get_sql_statistics",
  "args": {"sql_id": "8f3abc"},
  "duration_ms": 132,
  "status": "success"
}
```

Audit log entries are **always written**, even on errors. The `AuditContext` context manager guarantees this.
