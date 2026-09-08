# ARCHITECTURE — Technical Architecture Document
# Tài Liệu Kiến Trúc Kỹ Thuật

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Trạng thái / Status:** Draft  
**Ngày / Date:** 2026-09-08

> **Ưu tiên Tech Stack:** `hld.md` và `project_struct.md` là nguồn chính xác nhất.  
> **Tech Stack Priority:** `hld.md` and `project_struct.md` are the authoritative sources.

---

> 🇻🇳 **Phần tiếng Việt** — Sections 1–15  
> 🇬🇧 **English Section** — Sections 16–30

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tech Stack Tổng Quan

### 1.1 Stack Chính

| Layer | Công nghệ | Lý do |
|---|---|---|
| **API Server** | **FastAPI (Python)** | Async, type hints, auto OpenAPI docs, phù hợp AI workloads |
| **Oracle Access** | **`python-oracledb`** (thin mode) | Oracle official Python driver, không cần Oracle Client |
| **Evidence Store** | **PostgreSQL** | Reliable, JSON support, mature ecosystem |
| **MCP Server** | **Python** (`mcp/server.py`) | Cùng runtime với backend, dễ tích hợp |
| **AI/LLM** | **Python abstraction** (`ai/providers/`) | Multi-provider: OpenAI, Claude, Gemini |
| **Scheduler** | **APScheduler** | Background jobs (collection, daily report) |
| **Frontend** | **React** | Dashboard, Investigation UI |
| **Containerization** | **Docker / Docker Compose** | Reproducible dev & prod environment |
| **Package Manager** | **`pyproject.toml` (Poetry/uv)** | Modern Python packaging |

### 1.2 Tech Stack KHÔNG dùng

| Không dùng | Lý do |
|---|---|
| ~~.NET / C# / ASP.NET~~ | Tech stack đã thay đổi sang Python |
| ~~ODP.NET~~ | Thay bằng `python-oracledb` |
| ~~ILLMProvider (C# interface)~~ | Thay bằng Python abstract class |
| ~~Background Workers (.NET)~~ | Thay bằng APScheduler |

---

## 2. Kiến Trúc Tổng Thể (từ hld.md)

```
┌───────────────────────────────────────────────────────────┐
│                       DB COPILOT                          │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    React UI                         │  │
│  │                                                     │  │
│  │ Dashboard | Incidents | SQL | Investigation | Chat  │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   FastAPI                            │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Application Layer                       │  │
│  │                                                     │  │
│  │  Investigation Engine                               │  │
│  │  Incident Engine                                    │  │
│  │  Report Engine                                      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│              ┌──────────┴──────────┐                      │
│              ▼                     ▼                      │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ Correlation Engine   │  │ AI / LLM Service          │  │
│  └──────────┬──────────┘  └───────────────────────────┘  │
│             │                                             │
│             ▼                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Oracle Evidence Layer                   │  │
│  │                                                     │  │
│  │ Data Access → Normalization → Evidence Builder      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                Oracle MCP Server                     │  │
│  └──────────────────────┬──────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Oracle    │
                   │  Database   │
                   └─────────────┘

                          │
                          ▼

                   ┌─────────────┐
                   │ PostgreSQL  │
                   │  Evidence   │
                   │   Store     │
                   └─────────────┘
```

---

## 3. Cấu Trúc Dự Án (từ project_struct.md)

```
db-copilot/
│
├── src/
│
│   └── db_copilot/
│
│       ├── api/                    # FastAPI routes & app
│       │   ├── routes/
│       │   │   ├── health.py       # GET /health, GET /incidents
│       │   │   ├── investigation.py # POST /investigate
│       │   │   ├── sql.py          # GET /sql/{sql_id}
│       │   │   ├── reports.py      # GET /reports/daily
│       │   │   └── mcp.py          # MCP tool call proxy
│       │   ├── dependencies.py     # FastAPI Depends
│       │   └── app.py              # FastAPI app factory
│       │
│       ├── domain/                 # Domain models (no infra deps)
│       │   ├── models/
│       │   │   ├── incident.py
│       │   │   ├── evidence.py
│       │   │   ├── diagnosis.py
│       │   │   └── sql_metric.py
│       │   ├── enums/
│       │   │   ├── severity.py
│       │   │   └── incident_category.py
│       │   └── interfaces/
│       │       ├── llm_provider.py  # Abstract LLM interface
│       │       └── evidence_repo.py
│       │
│       ├── application/            # Use cases / business logic
│       │   ├── services/
│       │   │   ├── investigation_service.py
│       │   │   ├── health_service.py
│       │   │   └── report_service.py
│       │   ├── commands/
│       │   └── queries/
│       │
│       ├── oracle/                 # Oracle data access
│       │   ├── connection.py       # python-oracledb connection factory
│       │   ├── repositories/
│       │   │   ├── sql_repository.py
│       │   │   ├── session_repository.py
│       │   │   ├── awr_repository.py
│       │   │   ├── storage_repository.py
│       │   │   └── code_repository.py
│       │   └── queries/            # Raw SQL query strings
│       │       ├── sql_queries.py
│       │       ├── awr_queries.py
│       │       └── code_queries.py
│       │
│       ├── mcp/                    # MCP Server
│       │   ├── server.py           # MCP server entry point
│       │   └── tools/
│       │       ├── sql_tools.py    # Group 1: SQL tools
│       │       ├── session_tools.py # Group 2: Session tools
│       │       ├── awr_tools.py    # Group 3: AWR/ASH tools
│       │       ├── storage_tools.py # Group 4: Storage tools
│       │       ├── job_tools.py    # Group 5: Job tools
│       │       ├── health_tools.py  # Group 6: DB health tools
│       │       └── code_tools.py   # Group 7: Code intelligence
│       │
│       ├── evidence/               # Oracle Evidence Layer
│       │   ├── collectors/
│       │   │   ├── sql_collector.py
│       │   │   ├── session_collector.py
│       │   │   └── storage_collector.py
│       │   ├── normalizers/
│       │   │   └── evidence_normalizer.py
│       │   ├── builders/
│       │   │   └── evidence_builder.py
│       │   └── repository.py       # PostgreSQL evidence store
│       │
│       ├── correlation/            # Correlation Engine
│       │   ├── rules/
│       │   │   ├── sql_rules.py    # SQL regression, plan change
│       │   │   ├── session_rules.py # Blocking, long running
│       │   │   └── storage_rules.py # Tablespace threshold
│       │   ├── graph.py            # Evidence graph builder
│       │   └── engine.py           # Correlation orchestrator
│       │
│       ├── investigation/          # Investigation Engine
│       │   ├── planner.py          # Intent → Investigation plan
│       │   ├── executor.py         # Execute plan steps
│       │   └── context.py          # Investigation context state
│       │
│       ├── ai/                     # AI / LLM Service
│       │   ├── providers/
│       │   │   ├── openai_provider.py
│       │   │   ├── claude_provider.py
│       │   │   └── gemini_provider.py
│       │   ├── prompts/
│       │   │   ├── diagnosis_prompt.py
│       │   │   └── report_prompt.py
│       │   └── service.py          # AI service orchestrator
│       │
│       └── config/
│           ├── settings.py         # Pydantic Settings
│           └── logging.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── scenarios/                  # End-to-end scenarios
│
├── migrations/                     # PostgreSQL migrations (Alembic)
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/
│   ├── BRD.md
│   ├── PRD.md
│   ├── SRS.md
│   └── ARCHITECTURE.md
│
├── pyproject.toml
└── README.md
```

---

## 4. Kiến Trúc MCP Server

### 4.1 Design Philosophy

MCP Server là **Oracle Observability & Evidence Gateway** — không phải generic SQL executor.

```
# KHÔNG làm thế này:
async def execute_sql(sql: str) -> list[dict]: ...

# Phải làm thế này:
async def get_sql_statistics(sql_id: str) -> SqlStatistics: ...
async def get_blocking_sessions() -> list[BlockingChain]: ...
```

Lý do:
- An toàn hơn (không thể SQL injection leo thang)
- Output có semantic structure cho AI hiểu
- Dễ audit và kiểm soát
- AI nhận structured evidence, không phải raw table data

### 4.2 MCP Transport

| Mode | Config | Dùng khi |
|---|---|---|
| **Stdio** | Default | MCP Client spawn process local |
| **SSE (HTTP)** | `MCP_TRANSPORT=sse` | Remote MCP client qua HTTP |

### 4.3 MCP Server Entry Point

```python
# src/db_copilot/mcp/server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from db_copilot.mcp.tools import sql_tools, session_tools, awr_tools
from db_copilot.mcp.tools import storage_tools, job_tools, health_tools, code_tools

app = Server("oracle-db-copilot")

# Register all tools
app.add_tools([
    *sql_tools.get_tools(),
    *session_tools.get_tools(),
    *awr_tools.get_tools(),
    *storage_tools.get_tools(),
    *job_tools.get_tools(),
    *health_tools.get_tools(),
    *code_tools.get_tools(),
])

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
```

### 4.4 Tool Implementation Pattern

```python
# src/db_copilot/mcp/tools/sql_tools.py

from mcp.types import Tool
from db_copilot.oracle.repositories.sql_repository import SqlRepository
from db_copilot.evidence.builders.evidence_builder import AuditLogger

async def get_sql_statistics(sql_id: str) -> dict:
    """
    Lấy cumulative statistics của một SQL_ID từ V$SQL và DBA_HIST_SQLSTAT.
    """
    async with AuditLogger(tool="get_sql_statistics", args={"sql_id": sql_id}):
        repo = SqlRepository()
        stats = await repo.get_sql_statistics(sql_id)
        return stats.model_dump()

def get_tools() -> list[Tool]:
    return [
        Tool(
            name="get_sql_statistics",
            description="Get cumulative execution statistics for a specific SQL_ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_id": {"type": "string", "description": "Oracle SQL_ID (13 chars)"}
                },
                "required": ["sql_id"]
            },
            fn=get_sql_statistics
        ),
        # ... other tools
    ]
```

---

## 5. Oracle Connection Architecture

```python
# src/db_copilot/oracle/connection.py

import oracledb
from db_copilot.config.settings import Settings

class OracleConnectionFactory:
    """
    Singleton connection pool.
    Dùng python-oracledb thin mode (không cần Oracle Client).
    Read-only: không có bất kỳ DML/DDL nào được phép.
    """

    _pool: oracledb.AsyncConnectionPool | None = None

    @classmethod
    async def get_pool(cls) -> oracledb.AsyncConnectionPool:
        if cls._pool is None:
            settings = Settings()
            cls._pool = await oracledb.create_pool_async(
                user=settings.oracle_user,
                password=settings.oracle_password,
                dsn=settings.oracle_dsn,
                min=2,
                max=10,
                increment=1
            )
        return cls._pool

    @classmethod
    async def get_connection(cls) -> oracledb.AsyncConnection:
        pool = await cls.get_pool()
        return await pool.acquire()
```

**Bảo mật:**
- Oracle credentials được đọc từ environment variables
- Credentials KHÔNG bao giờ được log hoặc gửi cho LLM
- Dùng connection pool để tái sử dụng kết nối

---

## 6. FastAPI Application Architecture

```python
# src/db_copilot/api/app.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from db_copilot.oracle.connection import OracleConnectionFactory
from db_copilot.api.routes import health, investigation, sql, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await OracleConnectionFactory.get_pool()
    yield
    # Shutdown
    pool = await OracleConnectionFactory.get_pool()
    await pool.close()

app = FastAPI(
    title="DB Copilot API",
    description="AI Database Observability & Investigation Platform",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(investigation.router, prefix="/api/v1")
app.include_router(sql.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
```

### 6.1 API Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/database/status` | Database health score + summary |
| `GET` | `/api/v1/incidents` | List incidents (with filters) |
| `GET` | `/api/v1/incidents/{id}` | Incident detail với evidence |
| `POST` | `/api/v1/investigate` | Start natural language investigation |
| `GET` | `/api/v1/investigate/{id}` | Get investigation result |
| `GET` | `/api/v1/sql/top` | Top SQL by metric |
| `GET` | `/api/v1/sql/{sql_id}` | SQL detail + plan + history |
| `GET` | `/api/v1/reports/daily` | Daily health report |
| `GET` | `/api/v1/reports/daily/{date}` | Report cho ngày cụ thể |

---

## 7. Evidence Layer Architecture

### 7.1 Data Flow

```
Oracle Database
      │
      ▼
Collector (APScheduler, mỗi 5 phút)
      │
      ▼
Normalizer (chuẩn hóa units, timestamps, types)
      │
      ▼
Evidence Builder (tạo Evidence objects với metadata)
      │
      ▼
PostgreSQL Evidence Store
      │
      ▼
Correlation Engine (phát hiện anomaly, liên kết evidence)
      │
      ▼
Incident Engine (tạo incident records)
```

### 7.2 Collector Implementation

```python
# src/db_copilot/evidence/collectors/sql_collector.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_copilot.oracle.repositories.sql_repository import SqlRepository
from db_copilot.evidence.repository import EvidenceRepository

class SqlCollector:
    def __init__(self, scheduler: AsyncIOScheduler):
        scheduler.add_job(
            self.collect,
            trigger="interval",
            minutes=5,
            id="sql_collector"
        )

    async def collect(self):
        oracle_repo = SqlRepository()
        evidence_repo = EvidenceRepository()

        # Lấy top SQL
        top_sql = await oracle_repo.get_top_sql(metric="elapsed_time", limit=50)

        # Normalize và lưu
        for sql in top_sql:
            metric = SqlMetric.from_oracle(sql)
            await evidence_repo.upsert_sql_metric(metric)
```

---

## 8. Correlation Engine Architecture

### 8.1 Detection Rules

```python
# src/db_copilot/correlation/rules/sql_rules.py

class SqlRegressionRule:
    """
    Phát hiện SQL regression bằng so sánh với 7-day baseline.
    Chạy sau mỗi chu kỳ collection (5 phút).
    Không dùng LLM — pure algorithmic.
    """

    async def evaluate(self, sql_id: str, current_metrics: SqlMetric) -> Incident | None:
        baseline = await self.baseline_repo.get(sql_id)

        if not baseline or not baseline.is_reliable:
            return None  # Không đủ data để đánh giá

        if current_metrics.elapsed_time_ms > baseline.mean_elapsed_ms * self.multiplier:
            return Incident(
                severity=Severity.HIGH,
                category=IncidentCategory.SQL_REGRESSION,
                title=f"SQL regression detected: {sql_id}",
                evidence=[
                    Evidence(
                        type=EvidenceType.SQL_REGRESSION,
                        data={
                            "sql_id": sql_id,
                            "current_elapsed_ms": current_metrics.elapsed_time_ms,
                            "baseline_avg_ms": baseline.mean_elapsed_ms,
                            "multiplier": current_metrics.elapsed_time_ms / baseline.mean_elapsed_ms
                        }
                    )
                ]
            )
        return None
```

### 8.2 Evidence Graph

```python
# src/db_copilot/correlation/graph.py

class EvidenceGraph:
    """
    Build directed evidence graph:
    Node: Entity (SQL, Procedure, Table, Session, etc.)
    Edge: Relationship (executes, uses, accesses, blocks, etc.)
    Weight: Temporal proximity + causal likelihood
    """

    def add_evidence(self, evidence: Evidence) -> None:
        ...

    def get_connected_entities(self, entity: Entity, depth: int = 2) -> list[Entity]:
        ...

    def get_causal_chain(self, root: Entity) -> list[CausalRelationship]:
        ...
```

---

## 9. AI Service Architecture

### 9.1 LLM Provider Interface

```python
# src/db_copilot/domain/interfaces/llm_provider.py

from abc import ABC, abstractmethod
from db_copilot.domain.models.diagnosis import DiagnosisResult, EvidencePackage

class LLMProvider(ABC):

    @abstractmethod
    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """
        Nhận evidence package, trả về structured diagnosis.
        Output PHẢI là DiagnosisResult (structured JSON).
        Không được trả về free-form text.
        """
        pass

    @abstractmethod
    async def generate_report_section(self, incidents: list, template: str) -> str:
        """
        Tạo một section của daily report.
        """
        pass
```

### 9.2 Provider Implementations

```python
# src/db_copilot/ai/providers/openai_provider.py

from openai import AsyncOpenAI
from db_copilot.domain.interfaces.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI()
        self.model = model

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},  # Structured output
            messages=[
                {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
                {"role": "user", "content": self._build_prompt(package)}
            ]
        )
        return DiagnosisResult.model_validate_json(response.choices[0].message.content)
```

### 9.3 Provider Selection

```python
# src/db_copilot/ai/service.py

def get_llm_provider(settings: Settings) -> LLMProvider:
    match settings.llm_provider:
        case "openai":
            return OpenAIProvider(model=settings.openai_model)
        case "claude":
            return ClaudeProvider(model=settings.claude_model)
        case "gemini":
            return GeminiProvider(model=settings.gemini_model)
        case _:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
```

---

## 10. Investigation Engine Architecture

### 10.1 Investigation Flow

```python
# src/db_copilot/investigation/executor.py

class InvestigationExecutor:

    async def execute(self, question: str) -> InvestigationResult:
        # 1. Parse intent
        intent = await self.intent_parser.parse(question)

        # 2. Create investigation plan
        plan = self.planner.create_plan(intent)

        # 3. Execute steps (với dynamic dependency)
        context = InvestigationContext()
        for step in plan.steps:
            result = await self._execute_step(step, context)
            context.add_result(step.name, result)

        # 4. Build evidence package
        evidence_package = self.evidence_builder.build(context)

        # 5. Generate hypotheses
        hypotheses = self.hypothesis_engine.rank(evidence_package)
        evidence_package.hypotheses = hypotheses

        # 6. AI diagnosis
        diagnosis = await self.ai_service.diagnose(evidence_package)

        return InvestigationResult(
            question=question,
            intent=intent,
            evidence=evidence_package.evidence,
            hypotheses=hypotheses,
            diagnosis=diagnosis
        )
```

### 10.2 Dynamic Step Dependencies

```python
# Ví dụ: Step 3 cần kết quả từ Step 2

plan = InvestigationPlan([
    Step("get_ash_sql_activity", args={"begin": t0, "end": t1}),
    Step("get_sql_statistics",
         args={"sql_id": DependsOn("get_ash_sql_activity", extract="top_sql_id")}),
    Step("get_sql_plan_history",
         args={"sql_id": DependsOn("get_sql_statistics", extract="sql_id")}),
])
```

---

## 11. Security Architecture

### 11.1 Credential Flow

```
User Request
    │
    ▼
FastAPI
    │ (no Oracle credentials here)
    ▼
Application Services
    │ (no Oracle credentials here)
    ▼
OracleConnectionFactory
    │ (reads from environment / secrets vault)
    ▼
Oracle Database (read-only user)
```

**Oracle credentials KHÔNG BAO GIỜ được:**
- Gửi lên LLM
- Log trong audit
- Xuất hiện trong API response
- Commit vào git

### 11.2 Environment Configuration

```python
# src/db_copilot/config/settings.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Oracle
    oracle_user: str
    oracle_password: str          # Từ env var ORACLE_PASSWORD
    oracle_dsn: str               # host:port/service_name

    # PostgreSQL
    postgres_url: str             # Từ env var POSTGRES_URL

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str           # Từ env var OPENAI_API_KEY

    # Collection
    collection_interval_minutes: int = 5
    baseline_days: int = 7
    sql_regression_multiplier: float = 3.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 11.3 Audit Logging

```python
# src/db_copilot/evidence/builders/evidence_builder.py

class AuditLogger:
    """Context manager đảm bảo mọi MCP call đều được audit."""

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        await self.audit_repo.write(AuditRecord(
            tool_name=self.tool,
            input_args=self._sanitize(self.args),  # Remove sensitive data
            duration_ms=duration_ms,
            status="success" if exc_type is None else "error",
            error_message=str(exc_val) if exc_val else None
        ))
```

---

## 12. PostgreSQL Schema

```sql
-- Schema for Evidence Store

CREATE TABLE databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    host VARCHAR(256) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    version VARCHAR(32),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    captured_at TIMESTAMPTZ NOT NULL,
    active_sessions INT,
    blocking_sessions INT,
    cpu_pct DECIMAL(5,2),
    health_score INT,
    raw_data JSONB,
    INDEX idx_snapshots_db_time (database_id, captured_at DESC)
);

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
    plan_hash_value BIGINT,
    INDEX idx_sql_metrics_sql_time (database_id, sql_id, captured_at DESC)
);

CREATE TABLE sql_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    sql_id VARCHAR(13) NOT NULL,
    hour_of_day INT NOT NULL,
    day_of_week INT NOT NULL,
    sample_count INT,
    mean_elapsed_ms DECIMAL(15,2),
    stddev_elapsed_ms DECIMAL(15,2),
    p50_elapsed_ms DECIMAL(15,2),
    p95_elapsed_ms DECIMAL(15,2),
    is_reliable BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(database_id, sql_id, hour_of_day, day_of_week)
);

CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES databases(id),
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    severity VARCHAR(16),
    category VARCHAR(64),
    title TEXT,
    description TEXT,
    status VARCHAR(32) DEFAULT 'OPEN',
    diagnosis JSONB,
    INDEX idx_incidents_db_severity (database_id, severity, detected_at DESC)
);

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

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(128),
    database_id UUID REFERENCES databases(id),
    tool_name VARCHAR(128) NOT NULL,
    input_args JSONB,
    duration_ms INT,
    rows_returned INT,
    status VARCHAR(16),
    error_message TEXT,
    INDEX idx_audit_logs_time (occurred_at DESC)
);

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

## 13. Deployment Architecture

### 13.1 Docker Compose (Development)

```yaml
# docker/docker-compose.yml

version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ORACLE_USER=${ORACLE_USER}
      - ORACLE_PASSWORD=${ORACLE_PASSWORD}
      - ORACLE_DSN=${ORACLE_DSN}
      - POSTGRES_URL=postgresql+asyncpg://dbcopilot:secret@postgres/dbcopilot
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy

  mcp-server:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: python -m db_copilot.mcp.server
    environment:
      - ORACLE_USER=${ORACLE_USER}
      - ORACLE_PASSWORD=${ORACLE_PASSWORD}
      - ORACLE_DSN=${ORACLE_DSN}
    stdin_open: true
    tty: true

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: dbcopilot
      POSTGRES_USER: dbcopilot
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dbcopilot"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 13.2 Dockerfile

```dockerfile
# docker/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install system deps (libaio for python-oracledb thin mode — not needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "db_copilot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 14. Source Code Historical Limitation

### 14.1 MVP Constraint

MVP chỉ có thể đọc **source code hiện tại** từ `ALL_SOURCE`.

```
ALL_SOURCE
    │
    ▼
Parser → Extract SQL statements
    │
    ▼
Map SQL_ID → Source Line (best effort)
    │
    ▼
mapping_state: exact | inferred | unavailable
```

### 14.2 Future: Full Traceability

```
Oracle Source (current)
        +
Git history (PR/commit metadata)
        +
Deployment records (version, timestamp)
        ↓
Code → Performance Correlation
```

**Luôn ghi rõ trong output:**
- `mapping_state: "unavailable"` nếu không map được
- Không suy đoán "code change caused regression" khi thiếu deployment data

---

## 15. Kiến Trúc Dài Hạn (Long-term Architecture)

### 15.1 Multi-Agent System

```
                         ┌───────────────┐
                         │     User      │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │  DB Copilot   │
                         └───────┬───────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
      Health Agent (Python) Investigation Agent  Report Agent
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 │
                         Evidence Engine
                                 │
                         Oracle MCP Server (Python)
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
           Oracle               Git             Deployment
         Database             History            Records
```

### 15.2 Database Knowledge Graph (Future)

Entities và relationships được lưu trong graph database (Neo4j hoặc PostgreSQL với graph extensions):

```
Procedure ──executes──► SQL
SQL ──uses──────────► Plan
SQL ──accesses──────► Table
Table ──has──────────► Statistics
Deployment ──changes──► Procedure
Deployment ──contains──► GitCommit
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 16. Technology Stack Overview

### 16.1 Primary Stack

| Layer | Technology | Rationale |
|---|---|---|
| **API Server** | **FastAPI (Python)** | Async, type hints, auto OpenAPI docs, ideal for AI workloads |
| **Oracle Access** | **`python-oracledb`** (thin mode) | Oracle's official Python driver — no Oracle Client needed |
| **Evidence Store** | **PostgreSQL** | Reliable, JSON support, mature ecosystem |
| **MCP Server** | **Python** (`mcp/server.py`) | Same runtime as backend, easy integration |
| **AI/LLM** | **Python abstraction** (`ai/providers/`) | Multi-provider: OpenAI, Claude, Gemini |
| **Scheduler** | **APScheduler** | Background jobs (collection, daily report) |
| **Frontend** | **React** | Dashboard, Investigation UI |
| **Containerization** | **Docker / Docker Compose** | Reproducible dev & production |
| **Package Manager** | **`pyproject.toml` (Poetry/uv)** | Modern Python packaging |

### 16.2 Explicitly NOT Used

| Not Used | Reason |
|---|---|
| ~~.NET / C# / ASP.NET~~ | Tech stack changed to Python |
| ~~ODP.NET~~ | Replaced by `python-oracledb` |
| ~~C# Interfaces~~ | Replaced by Python abstract classes |
| ~~.NET Background Workers~~ | Replaced by APScheduler |

---

## 17. High-Level Architecture (from hld.md)

```
┌───────────────────────────────────────────────────────────┐
│                       DB COPILOT                          │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    React UI                         │  │
│  │ Dashboard | Incidents | SQL | Investigation | Chat  │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   FastAPI                            │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Application Layer (Python)              │  │
│  │  Investigation Engine | Incident Engine | Report     │  │
│  └──────────────────────┬──────────────────────────────┘  │
│              ┌──────────┴──────────┐                      │
│              ▼                     ▼                      │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ Correlation Engine   │  │ AI / LLM Service          │  │
│  └──────────┬──────────┘  └───────────────────────────┘  │
│             ▼                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Oracle Evidence Layer (Python)               │  │
│  │ Data Access → Normalization → Evidence Builder       │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Oracle MCP Server (Python)                  │  │
│  └──────────────────────┬──────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────┘
                          ▼
                   Oracle Database
                          ▼
                   PostgreSQL (Evidence Store)
```

---

## 18. Project Structure (from project_struct.md)

_(See Section 3 above — identical structure)_

Key directories:
- `db_copilot/api/` — FastAPI routes
- `db_copilot/oracle/` — Oracle data access via python-oracledb
- `db_copilot/mcp/` — MCP Server & tools
- `db_copilot/evidence/` — Evidence collection & storage
- `db_copilot/correlation/` — Detection rules & evidence graph
- `db_copilot/investigation/` — Investigation engine pipeline
- `db_copilot/ai/` — LLM providers & prompts
- `db_copilot/domain/` — Domain models & interfaces

---

## 19. MCP Server Architecture

### 19.1 Design Principle

MCP Server is an **Oracle Observability & Evidence Gateway** — NOT a generic SQL executor.

Semantic tools return structured data:
```python
# CORRECT: Semantic, structured
async def get_blocking_sessions() -> list[BlockingChain]: ...

# WRONG: Generic, unsafe
async def execute_sql(sql: str) -> list[dict]: ...
```

### 19.2 Tool Registration

```python
# src/db_copilot/mcp/server.py

app = Server("oracle-db-copilot")
app.add_tools([
    *sql_tools.get_tools(),      # 6 SQL tools
    *session_tools.get_tools(),  # 5 Session tools
    *awr_tools.get_tools(),      # 5 AWR/ASH tools
    *storage_tools.get_tools(),  # 5 Storage tools
    *job_tools.get_tools(),      # 4 Job tools
    *health_tools.get_tools(),   # 6 DB health tools
    *code_tools.get_tools(),     # 9 Code intelligence tools
])
```

---

## 20. Oracle Connection

Uses **`python-oracledb`** in **thin mode** (no Oracle Client installation required):

```python
pool = await oracledb.create_pool_async(
    user=settings.oracle_user,
    password=settings.oracle_password,
    dsn=settings.oracle_dsn,    # host:port/service_name
    min=2, max=10, increment=1
)
```

Security:
- Credentials from environment variables only
- Never logged, never sent to LLM
- Connection pool for efficient reuse

---

## 21. FastAPI API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/database/status` | DB health score + summary |
| `GET` | `/api/v1/incidents` | List incidents |
| `GET` | `/api/v1/incidents/{id}` | Incident detail with evidence |
| `POST` | `/api/v1/investigate` | Start natural language investigation |
| `GET` | `/api/v1/investigate/{id}` | Get investigation result |
| `GET` | `/api/v1/sql/top` | Top SQL by metric |
| `GET` | `/api/v1/sql/{sql_id}` | SQL detail + plan + history |
| `GET` | `/api/v1/reports/daily` | Latest daily health report |
| `GET` | `/api/v1/reports/daily/{date}` | Report for specific date |

---

## 22. LLM Provider Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """Must return structured DiagnosisResult — no free-form text."""
        pass
```

Implementations: `OpenAIProvider`, `ClaudeProvider`, `GeminiProvider`  
Selected via `settings.llm_provider` config.

---

## 23. Security Architecture

**Credential flow (credentials never reach AI layer):**
```
FastAPI → App Services → OracleConnectionFactory
    (reads from env)           ↓
                       Oracle Database (read-only user)
```

**Audit logging:** Every MCP tool call logged with timestamp, tool, args (sanitized), duration, status.

**Oracle permissions:** SELECT-only on ~30 pre-approved views. No DML, DDL, EXECUTE, or DBA role.

---

## 24. Deployment

**Docker Compose** for local development:
- `api` service: FastAPI on port 8000
- `mcp-server` service: Stdio MCP server
- `postgres` service: PostgreSQL 16

**Production:** Container orchestration (Kubernetes or Docker Swarm) with secrets management (e.g., HashiCorp Vault, AWS Secrets Manager) for Oracle credentials.

---

## 25. Long-term Architecture

### 25.1 Multi-Agent System

Health Agent, Investigation Agent, Report Agent operate in parallel, sharing the Evidence Engine, connecting to Oracle, Git, Deployment records.

### 25.2 Knowledge Graph (Future)

Entity graph: Database → Instance → SQL → Plan → Procedure → Package → Table → Index → Statistics → Deployment → Git Commit

Enables: *"What changed before this incident?"*
