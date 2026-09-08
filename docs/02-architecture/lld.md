# LLD — Low-Level Design
# Thiết Kế Cấp Thấp

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Project Structure Chi Tiết

### 1.1 oracle-mcp-server

```
oracle-mcp-server/
│
├── src/
│   └── oracle_mcp/
│       ├── server.py              # MCP server entry point (Stdio/SSE)
│       │
│       ├── tools/                 # MCP tool implementations
│       │   ├── sql.py             # get_top_sql, get_sql_statistics, get_sql_plan
│       │   ├── ash.py             # get_ash_sample, get_ash_sql_activity
│       │   ├── awr.py             # get_awr_snapshot, get_awr_sql_stats, get_awr_sql_plan
│       │   ├── session.py         # get_active_sessions, get_blocking_sessions, get_long_running_sessions
│       │   ├── plan.py            # get_sql_plan_history, get_sql_execution_context
│       │   ├── object.py          # get_object_source, get_object_metadata, get_object_dependencies
│       │   └── storage.py         # get_tablespace_usage, get_temp_usage, get_undo_usage, get_segment_growth
│       │
│       ├── oracle/
│       │   ├── connection.py      # python-oracledb async connection pool
│       │   ├── repositories/
│       │   │   ├── sql_repo.py
│       │   │   ├── ash_repo.py
│       │   │   ├── awr_repo.py
│       │   │   ├── session_repo.py
│       │   │   ├── plan_repo.py
│       │   │   ├── object_repo.py
│       │   │   └── storage_repo.py
│       │   └── queries/
│       │       ├── sql_queries.py
│       │       ├── ash_queries.py
│       │       ├── awr_queries.py
│       │       ├── session_queries.py
│       │       └── object_queries.py
│       │
│       ├── models/                # Pydantic response models
│       │   ├── sql_models.py
│       │   ├── session_models.py
│       │   ├── storage_models.py
│       │   └── object_models.py
│       │
│       ├── security/
│       │   ├── audit.py           # Audit logging (mọi MCP call)
│       │   └── sanitizer.py       # Sanitize args trước khi log
│       │
│       └── config/
│           └── settings.py        # Oracle DSN, credentials từ env vars
│
├── tests/
│   ├── unit/
│   └── integration/               # Cần Oracle test instance
│
├── docs/
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 1.2 db-copilot

```
db-copilot/
│
├── src/
│   └── db_copilot/
│       │
│       ├── api/                   # FastAPI application
│       │   ├── routes/
│       │   │   ├── health.py      # GET /health, GET /database/status
│       │   │   ├── incidents.py   # GET /incidents, GET /incidents/{id}
│       │   │   ├── investigation.py # POST /investigate, GET /investigate/{id}
│       │   │   ├── sql.py         # GET /sql/top, GET /sql/{sql_id}
│       │   │   └── reports.py     # GET /reports/daily, GET /reports/daily/{date}
│       │   ├── dependencies.py    # FastAPI Depends (settings, services)
│       │   └── app.py             # FastAPI factory, lifespan, middleware
│       │
│       ├── domain/                # Pure domain models — no infrastructure deps
│       │   ├── models/
│       │   │   ├── incident.py
│       │   │   ├── evidence.py
│       │   │   ├── diagnosis.py
│       │   │   ├── sql_metric.py
│       │   │   └── baseline.py
│       │   ├── enums/
│       │   │   ├── severity.py
│       │   │   ├── incident_category.py
│       │   │   └── evidence_type.py
│       │   └── interfaces/
│       │       ├── llm_provider.py
│       │       └── evidence_repo.py
│       │
│       ├── application/           # Use cases & orchestration
│       │   ├── services/
│       │   │   ├── investigation_service.py
│       │   │   ├── health_service.py
│       │   │   └── report_service.py
│       │   ├── commands/          # Write operations
│       │   └── queries/           # Read operations
│       │
│       ├── evidence/              # Oracle Evidence Layer
│       │   ├── collectors/
│       │   │   ├── sql_collector.py
│       │   │   ├── session_collector.py
│       │   │   └── storage_collector.py
│       │   ├── normalizers/
│       │   │   └── evidence_normalizer.py
│       │   ├── builders/
│       │   │   └── evidence_builder.py
│       │   └── repository.py      # PostgreSQL evidence store
│       │
│       ├── correlation/           # Detection & Correlation
│       │   ├── rules/
│       │   │   ├── sql_rules.py   # SQL regression, plan change
│       │   │   ├── session_rules.py # Blocking, long running
│       │   │   └── storage_rules.py # Tablespace threshold
│       │   ├── graph.py           # Evidence graph builder
│       │   └── engine.py          # Correlation orchestrator
│       │
│       ├── investigation/         # Investigation Engine
│       │   ├── planner.py         # Intent → Investigation plan
│       │   ├── executor.py        # Execute plan steps via MCP
│       │   └── context.py         # Investigation context state
│       │
│       ├── ai/                    # AI / LLM Service
│       │   ├── providers/
│       │   │   ├── openai_provider.py
│       │   │   ├── claude_provider.py
│       │   │   └── gemini_provider.py
│       │   ├── prompts/
│       │   │   ├── diagnosis_prompt.py
│       │   │   └── report_prompt.py
│       │   └── service.py
│       │
│       └── config/
│           ├── settings.py        # Pydantic Settings (env vars)
│           └── logging.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── scenarios/                 # End-to-end investigation scenarios
│
├── docs/
├── pyproject.toml
└── README.md
```

---

## 2. API Endpoints Chi Tiết

### FastAPI Routes

| Method | Path | Request | Response | Mô tả |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | — | `HealthStatus` | System health check |
| `GET` | `/api/v1/database/status` | — | `DatabaseStatus` | DB health score + summary |
| `GET` | `/api/v1/incidents` | `?severity=&status=&limit=` | `List[IncidentSummary]` | List incidents |
| `GET` | `/api/v1/incidents/{id}` | — | `IncidentDetail` | Incident + evidence |
| `POST` | `/api/v1/investigate` | `{question: str}` | `{id: str, status: "queued"}` | Start investigation |
| `GET` | `/api/v1/investigate/{id}` | — | `InvestigationResult` | Get investigation result |
| `GET` | `/api/v1/sql/top` | `?metric=elapsed&limit=20` | `List[SqlSummary]` | Top SQL |
| `GET` | `/api/v1/sql/{sql_id}` | — | `SqlDetail` | SQL detail + plan + history |
| `GET` | `/api/v1/reports/daily` | — | `DailyReport` | Latest daily report |
| `GET` | `/api/v1/reports/daily/{date}` | — | `DailyReport` | Report cho ngày cụ thể |

---

## 3. Domain Models Chi Tiết

### 3.1 Evidence

```python
@dataclass
class Evidence:
    id: UUID
    incident_id: UUID
    type: EvidenceType       # sql_plan_change, sql_regression, stale_statistics, ...
    source: str              # "DBA_HIST_SQLSTAT", "V$SESSION", etc.
    timestamp: datetime
    entity_type: str         # "SQL", "SESSION", "TABLE", "PROCEDURE"
    entity_id: str           # sql_id, session_id, object_name
    severity: Severity       # HIGH, MEDIUM, LOW, INFO
    data: dict               # Raw evidence payload
    supports_hypothesis: list[str]
```

### 3.2 Incident

```python
@dataclass
class Incident:
    id: UUID
    database_id: UUID
    detected_at: datetime
    resolved_at: datetime | None
    severity: Severity       # CRITICAL, HIGH, MEDIUM, LOW
    category: IncidentCategory  # SQL_REGRESSION, BLOCKING, TABLESPACE, JOB_FAILURE
    title: str
    description: str
    evidence: list[Evidence]
    diagnosis: Diagnosis | None
    status: IncidentStatus   # OPEN, INVESTIGATING, RESOLVED
```

### 3.3 DiagnosisResult

```python
@dataclass
class DiagnosisResult:
    diagnosis: str
    confidence: float        # 0.0 – 1.0
    primary_cause: str
    evidence_used: list[str]
    evidence_against: list[str]
    recommendations: list[Recommendation]
    confidence_explanation: str
    hypothesis_ranking: list[Hypothesis]
```

---

## 4. PostgreSQL Schema

### Core Tables

```sql
-- Databases being monitored
CREATE TABLE databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) UNIQUE NOT NULL,
    host VARCHAR(256) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    version VARCHAR(32),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Periodic health snapshots (every 5 min)
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    captured_at TIMESTAMPTZ NOT NULL,
    active_sessions INT,
    blocking_sessions INT,
    cpu_pct DECIMAL(5,2),
    health_score INT,
    raw_data JSONB
);
CREATE INDEX idx_snapshots_db_time ON snapshots(database_id, captured_at DESC);

-- SQL performance metrics per snapshot
CREATE TABLE sql_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    snapshot_id UUID REFERENCES snapshots(id),
    sql_id VARCHAR(13) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    executions BIGINT,
    elapsed_time_ms BIGINT,
    cpu_time_ms BIGINT,
    buffer_gets BIGINT,
    disk_reads BIGINT,
    rows_processed BIGINT,
    plan_hash_value BIGINT
);
CREATE INDEX idx_sql_metrics_id_time ON sql_metrics(database_id, sql_id, captured_at DESC);

-- SQL baselines (recalculated hourly)
CREATE TABLE sql_baselines (
    database_id UUID REFERENCES databases(id),
    sql_id VARCHAR(13) NOT NULL,
    hour_of_day INT NOT NULL,    -- 0-23
    day_of_week INT NOT NULL,    -- 0-6 (Mon-Sun)
    sample_count INT,
    mean_elapsed_ms DECIMAL(15,2),
    stddev_elapsed_ms DECIMAL(15,2),
    p50_elapsed_ms DECIMAL(15,2),
    p95_elapsed_ms DECIMAL(15,2),
    is_reliable BOOLEAN DEFAULT FALSE,  -- True khi sample_count >= 5
    calculated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (database_id, sql_id, hour_of_day, day_of_week)
);

-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    severity VARCHAR(16),       -- CRITICAL, HIGH, MEDIUM, LOW
    category VARCHAR(64),       -- SQL_REGRESSION, BLOCKING, TABLESPACE, JOB_FAILURE
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(32) DEFAULT 'OPEN',
    diagnosis JSONB
);
CREATE INDEX idx_incidents_db_sev ON incidents(database_id, severity, detected_at DESC);

-- Evidence items
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id),
    type VARCHAR(64),
    source VARCHAR(128),
    timestamp TIMESTAMPTZ,
    entity_type VARCHAR(32),
    entity_id VARCHAR(128),
    severity VARCHAR(16),
    data JSONB
);

-- MCP audit log (from db-copilot perspective — calls to oracle-mcp-server)
CREATE TABLE mcp_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    database_id UUID REFERENCES databases(id),
    tool_name VARCHAR(128) NOT NULL,
    input_args JSONB,           -- Sanitized, no credentials
    duration_ms INT,
    rows_returned INT,
    status VARCHAR(16),         -- success | error | timeout
    error_message TEXT
);
CREATE INDEX idx_audit_time ON mcp_audit_log(occurred_at DESC);

-- Daily reports
CREATE TABLE daily_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    report_date DATE NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    health_score INT,
    content_markdown TEXT,
    content_json JSONB,
    UNIQUE(database_id, report_date)
);
```

---

## 5. MCP Client trong db-copilot

db-copilot gọi oracle-mcp-server như một MCP client:

```python
# src/db_copilot/evidence/collectors/base_collector.py

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class OracleMcpClient:
    """
    MCP client để gọi oracle-mcp-server.
    db-copilot không biết Oracle credentials.
    """

    def __init__(self, mcp_command: str, mcp_args: list[str]):
        self.server_params = StdioServerParameters(
            command=mcp_command,
            args=mcp_args,
            # Oracle credentials được truyền qua env vars của oracle-mcp-server process
            env={
                "ORACLE_USER": settings.oracle_mcp_user,
                "ORACLE_PASSWORD": settings.oracle_mcp_password,
                "ORACLE_DSN": settings.oracle_mcp_dsn
            }
        )

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content
```

---

## 6. Configuration Schema

### oracle-mcp-server `.env`

```env
# Oracle connection (chỉ trong oracle-mcp-server)
ORACLE_USER=db_copilot_readonly
ORACLE_PASSWORD=<secret>
ORACLE_DSN=prod-oracle-host:1521/ORCL

# MCP transport mode
MCP_TRANSPORT=stdio  # hoặc sse
MCP_SSE_PORT=8080    # Chỉ dùng khi MCP_TRANSPORT=sse

# Audit
AUDIT_LOG_LEVEL=INFO
```

### db-copilot `.env`

```env
# MCP server connection
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=-m,oracle_mcp.server
MCP_SERVER_ENV_ORACLE_USER=db_copilot_readonly
MCP_SERVER_ENV_ORACLE_PASSWORD=<secret>
MCP_SERVER_ENV_ORACLE_DSN=prod-oracle-host:1521/ORCL

# PostgreSQL Evidence Store
POSTGRES_URL=postgresql+asyncpg://dbcopilot:secret@localhost/dbcopilot

# LLM
LLM_PROVIDER=openai  # openai | claude | gemini
OPENAI_API_KEY=<secret>
OPENAI_MODEL=gpt-4o

# Collection
COLLECTION_INTERVAL_MINUTES=5
BASELINE_DAYS=7
SQL_REGRESSION_MULTIPLIER=3.0
TABLESPACE_WARNING_THRESHOLD=80
TABLESPACE_CRITICAL_THRESHOLD=90

# Report
REPORT_SCHEDULE=0 6 * * *

# Alerts
SLACK_WEBHOOK_URL=<optional>
EMAIL_SMTP_HOST=<optional>
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Project Structure Detail

_(See Sections 1.1 and 1.2 — same content)_

Key points:
- **oracle-mcp-server**: All Oracle connectivity. Stateless. Can be deployed independently.
- **db-copilot**: AI Application. No direct Oracle connection. Has PostgreSQL for evidence persistence.

---

## 8. API Endpoints

_(See Section 2 — same table)_

All endpoints return structured JSON. Investigation uses async pattern: POST returns ID, GET polls for result.

---

## 9. Domain Models

_(See Section 3 — same models)_

All domain models are pure Python dataclasses with no infrastructure dependencies, following clean architecture principles.

---

## 10. PostgreSQL Schema

_(See Section 4 — same DDL)_

Key design decisions:
- `sql_baselines` uses composite PK on `(database_id, sql_id, hour_of_day, day_of_week)` for time-bucketed baseline queries
- `evidence_items.data` is JSONB for flexibility across different evidence types
- All audit logs stored in `mcp_audit_log` — retained minimum 1 year

---

## 11. MCP Client Pattern

db-copilot acts as **MCP client** to oracle-mcp-server:
- Spawns oracle-mcp-server process (Stdio mode) or connects to running server (SSE mode)
- Oracle credentials passed as env vars to the spawned process — never stored in db-copilot
- All tool calls go through `OracleMcpClient.call_tool()`

---

## 12. Configuration

Two separate `.env` files:
1. `oracle-mcp-server/.env`: Oracle connection + MCP transport settings
2. `db-copilot/.env`: MCP server connection + PostgreSQL + LLM + scheduling
