# oracle-mcp-server

**Oracle Observability & Evidence Gateway** — a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes read-only Oracle Database tools to AI agents.

> **Security principle:** This server has `SELECT`-only access to Oracle. It cannot execute INSERT / UPDATE / DELETE / DDL or any stored procedure.

---

## Architecture

```
AI Agent / MCP Client (Claude, Cursor, db-copilot …)
        │
        │  MCP Protocol (stdio / SSE)
        ▼
oracle-mcp-server          ← this project
        │
        │  python-oracledb (thin mode — no Oracle Client needed)
        ▼
  Oracle Database (read-only account)
```

---

## Phase 0 Tools (available now)

| Tool | Description |
|---|---|
| `get_database_info` | DB name, version, instance, host, startup time |
| `get_top_sql` | Top SQL by elapsed / CPU / IO / buffer gets / executions |
| `get_sql_statistics` | Full stats for a single SQL_ID |
| `get_active_sessions` | All active USER sessions |
| `get_blocking_sessions` | Blocking session chains (blocker → blocked tree) |
| `get_long_running_sessions` | Sessions running longer than N minutes |

---

## Requirements

- Python **3.12+**
- Oracle Database **12c+** (19c recommended)
- **No Oracle Instant Client** needed (uses `python-oracledb` thin mode)

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

**.env.example:**
```env
ORACLE_USER=db_copilot_readonly
ORACLE_PASSWORD=your_password_here
ORACLE_DSN=your-db-host:1521/ORCL
```

### 3. Create Oracle read-only account

Run the grants script in your Oracle instance as DBA:

```bash
# Edit the script to set the password first
sqlplus sys/password@ORCL as sysdba @docs/grants.sql
```

### 4. Run the server

```bash
# stdio mode (for local MCP clients)
python -m oracle_mcp.server

# or via installed script
oracle-mcp-server
```

### 5. Run tests

```bash
pytest tests/unit/ -v
```

---

## Configure with Claude Desktop

Add to `claude_desktop_config.json`:

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

Add to `.cursor/mcp.json`:

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
│   ├── server.py              # MCP server entry point
│   ├── tools/
│   │   ├── sql.py             # get_top_sql, get_sql_statistics
│   │   ├── session.py         # get_active_sessions, blocking, long-running
│   │   └── storage.py         # get_database_info
│   ├── oracle/
│   │   ├── connection.py      # Async connection pool (python-oracledb)
│   │   ├── repositories/      # Data access layer
│   │   └── queries/           # SQL query strings
│   ├── models/
│   │   └── response_models.py # Pydantic output schemas
│   ├── security/
│   │   ├── audit.py           # Audit logging (every tool call)
│   │   └── sanitizer.py       # Remove credentials from audit args
│   └── config/
│       └── settings.py        # Pydantic Settings (env vars)
│
├── tests/unit/                # Unit tests (no Oracle needed)
├── Dockerfile
└── pyproject.toml
```

---

## Security

- Oracle account has **SELECT-only** privileges on ~35 pre-approved views
- No DML, DDL, EXECUTE, or DBA role granted
- Oracle credentials only in environment variables — never logged, never sent to AI
- Every MCP tool call is audit-logged to stderr (JSON format)

---

## Audit Log Format

Every tool call emits one JSON line to stderr:

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
  "timestamp": "2026-09-08T14:32:01Z",
  "tool": "get_blocking_sessions",
  "args": {},
  "duration_ms": 45,
  "status": "error",
  "error": "ORA-00942: table or view does not exist"
}
```
