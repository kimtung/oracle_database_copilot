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

## 5. MCP Client trong db-copilot

Để đáp ứng SLA điều tra sự cố (< 60s cho chuỗi 9 bước investigation) và tuân thủ nguyên tắc an ninh bảo mật dữ liệu, `db-copilot` kết nối với `oracle-mcp-server` qua **SSE Transport với Persistent Connection** ([LLD-01], [LLD-02]).

### 5.1 Kiến trúc kết nối Persistent SSE
- **oracle-mcp-server** chạy độc lập dưới dạng microservice/daemon (Docker container hoặc systemd), quản lý Oracle Connection Pool và lưu giữ an toàn credentials nội bộ.
- **db-copilot** là SSE client, kết nối qua HTTP/SSE (`MCP_SERVER_URL`). `db-copilot` hoàn toàn **không lưu trữ hoặc chuyển tiếp** tài khoản Oracle (`ORACLE_USER`/`ORACLE_PASSWORD`).
- **Tái sử dụng Connection/Session**: `OracleMcpClient` khởi tạo `ClientSession` một lần trong vòng đời ứng dụng (hoặc phiên điều tra), loại bỏ hoàn toàn chi phí khởi động tiến trình Python (~1.5s) và bắt tay kết nối Oracle (~1s) ở mỗi tool call. Thời gian thực thi mỗi tool call giảm từ ~2-3s xuống còn ~30-100ms.

### 5.2 Implementation Pattern (`OracleMcpClient`)

```python
# src/db_copilot/mcp/client.py

import json
import logging
import time
from typing import Any
from mcp import ClientSession
from mcp.client.sse import sse_client
from db_copilot.config.settings import get_settings

logger = logging.getLogger(__name__)

class McpClientError(Exception):
    """Ngoại lệ khi gọi MCP tool thất bại."""
    def __init__(self, tool_name: str, message: str, duration_ms: int = 0):
        super().__init__(f"MCP tool '{tool_name}' error: {message}")
        self.tool_name = tool_name
        self.message = message
        self.duration_ms = duration_ms

class OracleMcpClient:
    """
    Persistent SSE MCP Client kết nối tới oracle-mcp-server.
    db-copilot hoàn toàn không lưu giữ credentials của Oracle DB.
    """

    def __init__(self, server_url: str | None = None, auth_token: str | None = None):
        settings = get_settings()
        self.server_url = server_url or settings.mcp_server_url
        self.auth_token = auth_token or settings.mcp_server_auth_token
        self._session: ClientSession | None = None
        self._sse_ctx = None
        self._session_ctx = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self) -> None:
        """Khởi tạo persistent connection một lần duy nhất."""
        if self._session is not None:
            return

        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        self._sse_ctx = sse_client(self.server_url, headers=headers)
        read_stream, write_stream = await self._sse_ctx.__aenter__()

        self._session_ctx = ClientSession(read_stream, write_stream)
        self._session = await self._session_ctx.__aenter__()
        await self._session.initialize()
        logger.info(f"Connected persistent MCP SSE session to {self.server_url}")

    async def disconnect(self) -> None:
        """Đóng session và giải phóng kết nối SSE khi shutdown."""
        if self._session_ctx:
            await self._session_ctx.__aexit__(None, None, None)
            self._session_ctx = None
            self._session = None
        if self._sse_ctx:
            await self._sse_ctx.__aexit__(None, None, None)
            self._sse_ctx = None
        logger.info("Closed persistent MCP SSE session")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Gọi MCP tool trên session đã mở sẵn, tái sử dụng cho toàn bộ investigation."""
        if self._session is None:
            await self.connect()

        start_time = time.monotonic()
        arguments = arguments or {}

        try:
            result = await self._session.call_tool(tool_name, arguments=arguments)
            duration_ms = int((time.monotonic() - start_time) * 1000)

            if getattr(result, "isError", False):
                err_msg = self._extract_text(result.content)
                raise McpClientError(tool_name, err_msg, duration_ms=duration_ms)

            content_text = self._extract_text(result.content)
            logger.debug(f"Tool {tool_name} executed via SSE in {duration_ms}ms")
            
            try:
                return json.loads(content_text)
            except (json.JSONDecodeError, TypeError):
                return content_text

        except Exception as e:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            logger.error(f"MCP tool {tool_name} failed ({duration_ms}ms): {e}")
            raise McpClientError(tool_name, str(e), duration_ms=duration_ms) from e

    def _extract_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if hasattr(item, "text"):
                    parts.append(item.text)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
            return "\n".join(parts)
        return str(content) if content else ""
```

---

## 6. Configuration Schema & Trade-offs

### 6.1 oracle-mcp-server `.env`
*(Chứa toàn bộ cấu hình kết nối Oracle và bảo mật transport)*

```env
# Oracle Connection (Chỉ duy nhất oracle-mcp-server nắm giữ credentials)
ORACLE_USER=db_copilot_readonly
ORACLE_PASSWORD=<secret>
ORACLE_DSN=prod-oracle-host:1521/ORCL
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10

# MCP Transport Mode
MCP_TRANSPORT=sse
MCP_SSE_HOST=0.0.0.0
MCP_SSE_PORT=8080
MCP_SERVER_AUTH_TOKEN=<secret-internal-bearer-token>

# Audit Logging
AUDIT_LOG_LEVEL=INFO
AUDIT_RETENTION_DAYS=365
```

### 6.2 db-copilot `.env`
*(Tuyệt đối KHÔNG chứa Oracle credentials — giải quyết [LLD-02])*

```env
# MCP Server Connection (SSE Persistent Transport)
MCP_TRANSPORT=sse
MCP_SERVER_URL=http://oracle-mcp-server:8080/sse
MCP_SERVER_AUTH_TOKEN=<secret-internal-bearer-token>

# PostgreSQL Evidence Store
POSTGRES_URL=postgresql+asyncpg://dbcopilot:secret@localhost/dbcopilot

# LLM Provider Configuration
LLM_PROVIDER=openai  # openai | claude | gemini
OPENAI_API_KEY=<secret>
OPENAI_MODEL=gpt-4o

# Fallback LLM Provider (Optional)
FALLBACK_LLM_PROVIDER=gemini
GEMINI_API_KEY=<secret>
GEMINI_MODEL=gemini-2.0-flash

# Collection & Baselines
COLLECTION_INTERVAL_MINUTES=5
BASELINE_DAYS=7
SQL_REGRESSION_MULTIPLIER=3.0
TABLESPACE_WARNING_THRESHOLD=80
TABLESPACE_CRITICAL_THRESHOLD=90

# Daily Report
REPORT_SCHEDULE=0 6 * * *

# Alerts
SLACK_WEBHOOK_URL=<optional>
TEAMS_WEBHOOK_URL=<optional>
```

### 6.3 So Sánh & Trade-offs Các LLM Provider ([LLD-03])

Để hỗ trợ khách hàng doanh nghiệp (commercial customers) lựa chọn cấu hình phù hợp giữa **Chi phí (Cost)**, **Tốc độ (Latency)** và **Độ tin cậy JSON (Structured Output Reliability)**, hệ thống cung cấp ma trận đánh giá chi tiết:

| Tiêu chí | OpenAI `gpt-4o` *(Mặc định)* | Anthropic `claude-3-5-sonnet` | Google `gemini-2.0-flash` | OpenAI `gpt-4o-mini` | Google `gemini-1.5-pro` |
|---|---|---|---|---|---|
| **Chi phí Input (1M tokens)** | \$2.50 | \$3.00 | **\$0.10** | \$0.15 | \$1.25 |
| **Chi phí Output (1M tokens)** | \$10.00 | \$15.00 | **\$0.40** | \$0.60 | \$5.00 |
| **Độ trễ Latency (p50 / p95)** | ~1.2s / 2.5s | ~1.8s / 3.8s | **~0.6s / 1.2s** | ~0.5s / 1.0s | ~2.0s / 4.5s |
| **Độ tin cậy JSON Output** | ⭐⭐⭐⭐⭐ (Strict Mode) | ⭐⭐⭐⭐ (Cần parse markdown) | ⭐⭐⭐⭐⭐ (Structured Schema) | ⭐⭐⭐⭐⭐ (Strict Mode) | ⭐⭐⭐⭐⭐ (Structured Schema) |
| **Khả năng suy luận Oracle DB** | ⭐⭐⭐⭐⭐ (Rất chuẩn xác) | ⭐⭐⭐⭐⭐ (RCA xuất sắc nhất) | ⭐⭐⭐⭐ (Tốt) | ⭐⭐⭐ (Cơ bản) | ⭐⭐⭐⭐⭐ (Rất sâu) |
| **Context Window** | 128K tokens | 200K tokens | **1,048K tokens (1M)** | 128K tokens | **2,097K tokens (2M)** |
| **Phù hợp sử dụng** | **Production Tiêu chuẩn** | **Sự cố P1 / RCA Phức tạp** | **Chi phí tối ưu / High-traffic** | **Tóm tắt đơn giản / Dev** | **Phân tích AWR Dump lớn** |

#### Hướng Dẫn Lựa Chọn Kiến Trúc Cho Khách Hàng Doanh Nghiệp:
1. **Môi trường Production tiêu chuẩn (Khuyến nghị):** Chọn `LLM_PROVIDER=openai` với model `gpt-4o`. Lý do: Hỗ trợ Native Structured Outputs đảm bảo 100% schema JSON không bao giờ bị lỗi format khi parse vào `DiagnosisResult`.
2. **Tối ưu chi phí vận hành & Báo cáo định kỳ:** Chọn `LLM_PROVIDER=gemini` với model `gemini-2.0-flash`. Chi phí thấp hơn **25 lần** so với GPT-4o, tốc độ xử lý dưới 1 giây, context window 1M tokens cho phép nạp lượng lớn snapshot metric.
3. **Phân tích sự cố nghiêm trọng (Severity CRITICAL):** Cấu hình fallback hoặc định tuyến chuyên biệt sang `claude-3-5-sonnet`. Claude thể hiện khả năng liên kết nguyên nhân gốc rễ (Root Cause Analysis) tốt nhất trên execution plan phức tạp và chuỗi lock contention.

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Project Structure Detail

_(See Sections 1.1 and 1.2 — same content)_

Key points:
- **oracle-mcp-server**: All Oracle connectivity. Stateless daemon. Runs independently with internal credentials.
- **db-copilot**: AI Application. Connects to MCP server via SSE transport. Zero direct Oracle credentials. Has PostgreSQL for evidence persistence.

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
- **SSE Persistent Transport ([LLD-01])**: Reuses long-lived HTTP/SSE connection (`ClientSession`) across all tool calls in an investigation session, avoiding process spawn and connection pool overhead (~2-3s per call dropped to ~30-100ms), guaranteeing SLA < 60s.
- **Security Boundary ([LLD-02])**: Oracle credentials reside exclusively inside `oracle-mcp-server`. `db-copilot` only knows `MCP_SERVER_URL` (and bearer auth token), completely eliminating credential leakage into the AI application.
- All tool calls go through `OracleMcpClient.call_tool()`.

---

## 12. Configuration & LLM Provider Trade-offs

### 12.1 Configuration Isolation
Two separate `.env` files:
1. `oracle-mcp-server/.env`: Oracle connection (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`) + MCP SSE server settings.
2. `db-copilot/.env`: `MCP_SERVER_URL` + PostgreSQL + LLM API keys + scheduling (No Oracle credentials).

### 12.2 LLM Provider Comparison ([LLD-03])
- **OpenAI `gpt-4o` (Default)**: Best balance of Oracle SQL reasoning and guaranteed structured JSON outputs via Strict Mode.
- **Google `gemini-2.0-flash`**: Highest throughput, ultra-low latency (<1s), lowest cost (~25x cheaper), 1M token context for massive AWR/ASH dumps.
- **Anthropic `claude-3-5-sonnet`**: Superior root cause analysis for complex execution plan regressions and locking graphs. Recommended for Critical incidents.
