# oracle-mcp-server

**Oracle Observability & Evidence Gateway** — a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes **32 read-only Oracle Database tools** to AI agents (Claude, Cursor, db-copilot, ...).

> **Security principle:** This server has `SELECT`-only access to Oracle. It **cannot** execute `INSERT` / `UPDATE` / `DELETE` / `DDL` or any stored procedure. Oracle credentials are **never** sent to the LLM or written to audit logs.

---

## Architecture

```
AI Agent / MCP Client
(Claude Desktop, Cursor, db-copilot …)
        │
        │  MCP Protocol (stdio / SSE)   ← MCP SDK 2.x
        ▼
oracle-mcp-server          ← this project
        │
        │  oracledb (thin mode — no Oracle Client needed)
        │  async connection pool
        ▼
  Oracle Database (read-only account: db_copilot_readonly)
```

---

## Implemented Tools (32 / 32)

### 🔍 SQL Performance (4 tools)

| Tool | Description | Source |
|---|---|---|
| `get_top_sql` | Top SQL ranked by `elapsed_time` \| `cpu` \| `io` \| `buffer_gets` \| `executions` | `V$SQLSTATS` |
| `get_sql_statistics` | Full cumulative stats for a single SQL_ID (avg elapsed, CPU, buffer gets, disk reads) | `V$SQL` |
| `get_sql_wait_events` | Aggregated wait events for a SQL_ID in a time window | `V$ACTIVE_SESSION_HISTORY` |
| `get_sql_execution_context` | Module / action / program calling a SQL_ID and how often | `V$ACTIVE_SESSION_HISTORY` |

### ⏱ Active Session History — Real-time (2 tools)

| Tool | Description | Source |
|---|---|---|
| `get_ash_sample` | ASH samples for a time range (flexible ISO-8601 or `hours` shortcut) | `V$ACTIVE_SESSION_HISTORY` |
| `get_ash_sql_activity` | Historical ASH activity for a specific SQL_ID | `DBA_HIST_ACTIVE_SESS_HISTORY` |

### 📦 AWR — Historical (2 tools)

| Tool | Description | Source |
|---|---|---|
| `get_awr_snapshot` | List AWR snapshot intervals | `DBA_HIST_SNAPSHOT` |
| `get_awr_sql_stats` | Per-snapshot stats for a SQL_ID (rolling days or snap range) | `DBA_HIST_SQLSTAT` |

### 👥 Sessions (5 tools)

| Tool | Description | Source |
|---|---|---|
| `get_active_sessions` | All active USER sessions, filterable by elapsed time | `V$SESSION` |
| `get_session` | Full detail for a specific session (SID + SERIAL#) | `V$SESSION` |
| `get_session_waits` | Current wait event details with P1/P2/P3 parameters | `V$SESSION_WAIT` |
| `get_blocking_sessions` | Blocking chain tree: blocker → blocked sessions | `V$SESSION` |
| `get_long_running_sessions` | Sessions running longer than N minutes | `V$SESSION` |

### 📋 Execution Plans (2 tools)

| Tool | Description | Source |
|---|---|---|
| `get_sql_plan` | Current execution plan with predicates and cost | `V$SQL_PLAN` |
| `get_sql_plan_history` | Distinct plans seen in AWR — detects plan regressions | `DBA_HIST_SQL_PLAN` + `DBA_HIST_SQLSTAT` |

### 🔧 PL/SQL Objects & Code (6 tools)

| Tool | Description | Source |
|---|---|---|
| `get_object_source` | Full PL/SQL source code for PROCEDURE / FUNCTION / PACKAGE / TRIGGER | `ALL_SOURCE`, `DBA_OBJECTS` |
| `get_object_metadata` | Object metadata including `stale_stats`, `last_analyzed` | `DBA_OBJECTS`, `DBA_TAB_STATISTICS` |
| `get_object_arguments` | Parameter list for a stored procedure or function | `ALL_ARGUMENTS` |
| `get_object_dependencies` | Direct dependencies of a database object | `ALL_DEPENDENCIES` |
| `get_dependency_graph` | Recursive dependency graph up to N levels deep | `ALL_DEPENDENCIES` (CTE) |
| `get_invalid_objects` | All INVALID PL/SQL objects in the database | `DBA_OBJECTS` |

### 🗄 Storage, Health & Scheduler (11 tools)

| Tool | Description | Source |
|---|---|---|
| `get_database_info` | DB name, version, instance name, host, startup time, log mode | `V$DATABASE`, `V$INSTANCE` |
| `get_tablespace_usage` | Used% + used/free bytes for all tablespaces | `DBA_TABLESPACES`, `DBA_DATA_FILES`, `DBA_FREE_SPACE` |
| `get_datafile_usage` | Individual datafile details for a tablespace | `DBA_DATA_FILES` |
| `get_segment_growth` | Current size (bytes, blocks, extents) for a table/index/LOB | `DBA_SEGMENTS` |
| `get_temp_usage` | TEMP tablespace current usage | `DBA_TEMP_FILES`, `V$TEMPSTAT` |
| `get_undo_usage` | UNDO statistics: active/unexpired/expired blocks, tuned retention | `V$UNDOSTAT` |
| `get_redo_statistics` | Online redo log status + archived log generation rate by hour | `V$LOG`, `V$ARCHIVED_LOG` |
| `get_resource_usage` | Key system stats: physical reads/writes, commits, parses, long scans | `V$SYSSTAT` |
| `get_scheduler_jobs` | All Oracle Scheduler jobs with state, failure count, next run | `DBA_SCHEDULER_JOBS` |
| `get_scheduler_job_history` | Execution history for a specific scheduler job | `DBA_SCHEDULER_JOB_RUN_DETAILS` |
| `get_failed_jobs` | All scheduler jobs that failed in the last N hours | `DBA_SCHEDULER_JOB_RUN_DETAILS` |

---

## Requirements

- Python **3.12+**
- Oracle Database **12c+** (19c recommended)
- **No Oracle Instant Client** needed — uses `oracledb` thin mode

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/kimtung/oracle_database_copilot.git
cd oracle_database_copilot/oracle-mcp-server
pip install -e ".[dev]"
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Oracle credentials
```

**`.env` variables:**

```env
# Required
ORACLE_USER=db_copilot_readonly
ORACLE_PASSWORD=your_password_here
ORACLE_DSN=your-db-host:1521/ORCL

# Optional (defaults shown)
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10
ORACLE_POOL_INCREMENT=1
ORACLE_QUERY_TIMEOUT_SEC=30
MCP_TRANSPORT=stdio
```

### 3. Create Oracle read-only account (DBA required)

```bash
# Edit docs/grants.sql to set the password first
sqlplus sys/password@ORCL as sysdba @docs/grants.sql
```

This grants `SELECT` on ~40 pre-approved V$ views and DBA_HIST_ tables.
**No DML, DDL, EXECUTE, or DBA role is granted.**

### 4. Run the server

```bash
# Via installed script
oracle-mcp-server

# Or directly
python -m oracle_mcp.server
```

### 5. Run unit tests (no Oracle needed)

```bash
pytest tests/unit/ -v
# → 14 passed
```

---

## Configure with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "oracle-db": {
      "command": "python",
      "args": ["-m", "oracle_mcp.server"],
      "cwd": "/path/to/oracle-mcp-server",
      "env": {
        "ORACLE_USER": "db_copilot_readonly",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "db-host:1521/ORCL"
      }
    }
  }
}
```

## Configure with Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "oracle-db": {
      "command": "python",
      "args": ["-m", "oracle_mcp.server"],
      "env": {
        "ORACLE_USER": "db_copilot_readonly",
        "ORACLE_PASSWORD": "your_password",
        "ORACLE_DSN": "db-host:1521/ORCL"
      }
    }
  }
}
```

---

## Project Structure

```
oracle-mcp-server/
│
├── src/oracle_mcp/
│   ├── server.py                    # MCPServer entry point — 32 @mcp.tool() decorators
│   │
│   ├── tools/                       # Tool handlers (thin layer: validate → repo → audit)
│   │   ├── sql.py                   # get_top_sql, get_sql_statistics, get_sql_wait_events,
│   │   │                            #   get_sql_execution_context
│   │   ├── ash.py                   # get_ash_sample, get_ash_sql_activity
│   │   ├── awr.py                   # get_awr_snapshot, get_awr_sql_stats
│   │   ├── session.py               # get_active_sessions, get_session, get_session_waits,
│   │   │                            #   get_blocking_sessions, get_long_running_sessions
│   │   ├── plan.py                  # get_sql_plan, get_sql_plan_history
│   │   ├── object.py                # get_object_source, get_object_metadata,
│   │   │                            #   get_object_arguments, get_object_dependencies,
│   │   │                            #   get_dependency_graph, get_invalid_objects
│   │   └── storage.py               # get_database_info, get_tablespace_usage,
│   │                                #   get_datafile_usage, get_segment_growth,
│   │                                #   get_temp_usage, get_undo_usage,
│   │                                #   get_redo_statistics, get_resource_usage,
│   │                                #   get_scheduler_jobs, get_scheduler_job_history,
│   │                                #   get_failed_jobs
│   │
│   ├── oracle/
│   │   ├── connection.py            # Async connection pool (oracledb thin mode)
│   │   ├── repositories/
│   │   │   ├── base.py              # _fetchall / _fetchone helpers
│   │   │   ├── sql_repo.py          # SQL + session queries
│   │   │   ├── ash_repo.py          # ASH queries
│   │   │   ├── awr_repo.py          # AWR queries
│   │   │   ├── object_repo.py       # Plan + object/code queries
│   │   │   └── storage_repo.py      # Storage + scheduler queries
│   │   └── queries/
│   │       ├── sql_queries.py       # V$SQL, V$SQLSTATS, V$SESSION SQL strings
│   │       ├── ash_queries.py       # V$ASH, DBA_HIST_ASH SQL strings
│   │       ├── awr_queries.py       # DBA_HIST_SNAPSHOT, DBA_HIST_SQLSTAT SQL strings
│   │       ├── object_queries.py    # V$SQL_PLAN, ALL_SOURCE, ALL_DEPENDENCIES SQL strings
│   │       └── storage_queries.py   # DBA_TABLESPACES, V$LOG, DBA_SCHEDULER_JOBS SQL strings
│   │
│   ├── models/
│   │   └── response_models.py       # Pydantic output schemas (DatabaseInfo, SqlSummary, ...)
│   │
│   ├── security/
│   │   ├── audit.py                 # audit_context: JSON audit log every tool call
│   │   └── sanitizer.py             # Mask credentials before logging
│   │
│   └── config/
│       └── settings.py              # Pydantic Settings (lazy-loaded from env)
│
├── tests/
│   ├── conftest.py                  # Fake Oracle env for unit tests (no real DB needed)
│   └── unit/
│       └── test_phase0_tools.py     # 14 unit tests (mocked Oracle)
│
├── docs/
│   └── grants.sql                   # Oracle DBA script: create read-only account + grants
│
├── .env.example                     # Environment variable template
├── Dockerfile                       # python:3.12-slim, no Oracle Client needed
└── pyproject.toml                   # Build config, dependencies, pytest config
```

---

## Security

| Concern | How it's handled |
|---|---|
| Oracle credentials | Environment variables only — never hardcoded, never logged, never sent to LLM |
| Write access | Read-only Oracle account (`SELECT` only on ~40 pre-approved views) |
| Audit trail | Every tool call logs a JSON audit record to stderr (timestamp, tool, args, duration, status) |
| Credential scrubbing | `sanitizer.py` masks `password`, `secret`, `token`, `dsn` etc. from audit args |
| SQL injection | All Oracle queries use bind variables (`:param`) — no string interpolation |

---

## Audit Log Format

Every MCP tool call emits one JSON line to **stderr**:

```json
{
  "timestamp": "2026-09-08T14:32:01Z",
  "tool": "get_sql_statistics",
  "args": {"sql_id": "8f3abc"},
  "duration_ms": 132,
  "status": "success"
}
```

On error:
```json
{
  "timestamp": "2026-09-08T14:32:05Z",
  "tool": "get_blocking_sessions",
  "args": {},
  "duration_ms": 45,
  "status": "error",
  "error": "ORA-00942: table or view does not exist"
}
```

---

## Status

| Phase | Status |
|---|---|
| Phase 0 — Foundation (6 core tools) | ✅ Complete |
| Phase 1 — All 32 Tools | ✅ Complete |
| Phase 2 — db-copilot FastAPI app | 🔄 Planned |
| Phase 3 — AI Investigation Engine | 🔄 Planned |
