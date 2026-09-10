# 📌 SESSION STATE — Oracle DB Copilot
> Cập nhật lần cuối: 2026-09-10 22:45 (GMT+7)

---

## Cách resume session mới

1. Mở Antigravity IDE
2. Copy đoạn sau và paste vào chat:

```
@[SESSION_STATE.md] Đây là trạng thái dự án. Hãy đọc và tiếp tục từ mục "NEXT ACTION".
```

---

## Tổng quan dự án

**Tên:** Oracle Database Copilot  
**Mô tả:** AI-powered Oracle DBA assistant — phát hiện và chẩn đoán vấn đề hiệu năng tự động  
**Repo:** https://github.com/kimtung/oracle_database_copilot.git  
**Workspace:** `d:\2026\oracle_ai`  

### Hai project con
| Project | Thư mục | Mô tả |
|---|---|---|
| `oracle-mcp-server` | `d:\2026\oracle_ai\oracle-mcp-server\` | MCP server, read-only Oracle gateway, 32 tools |
| `db-copilot` | `d:\2026\oracle_ai\db-copilot\` | FastAPI app, PostgreSQL, AI engines (Foundation DONE) |

---

## ✅ ĐÃ HOÀN THÀNH

### 1. oracle-mcp-server (Phase 0 + Phase 1 DONE)

**Tech stack:**
- Python 3.13, MCP SDK 2.x (`MCPServer`, `@mcp.tool()`)
- `oracledb` 4.0.2 thin mode (không cần Oracle Instant Client)
- `pydantic`, `pydantic-settings` (lazy-load settings từ env)

**Files đã tạo:**
```
oracle-mcp-server/
├── pyproject.toml                          ← build config, deps
├── .env.example                            ← template env vars
├── Dockerfile                              ← python:3.12-slim
├── README.md                               ← đã cập nhật đầy đủ 32 tools
├── docs/
│   └── grants.sql                          ← Oracle DBA script tạo read-only account (tối ưu cho SE2)
├── src/oracle_mcp/
│   ├── server.py                           ← entry point, 32 tools registered
│   ├── config/settings.py                  ← Pydantic Settings (lazy)
│   ├── oracle/
│   │   ├── connection.py                   ← async pool
│   │   ├── queries/                        ← sql, ash, awr, object, storage queries
│   │   └── repositories/                   ← sql, ash, awr, object, storage repos
│   ├── tools/                              ← 32 tools (sql, ash, awr, session, plan, object, storage)
│   ├── models/response_models.py           ← Pydantic output schemas
│   └── security/                           ← audit logging + credential sanitizer
└── tests/
    ├── conftest.py                         ← fake Oracle env, no real DB needed
    └── unit/test_phase0_tools.py           ← 14 tests ✅ ALL PASSED
```

**32 tools đã implement:**
- **SQL (4):** `get_top_sql`, `get_sql_statistics`, `get_sql_wait_events`, `get_sql_execution_context`
- **ASH (2):** `get_ash_sample`, `get_ash_sql_activity`
- **AWR (2):** `get_awr_snapshot`, `get_awr_sql_stats`
- **Session (5):** `get_active_sessions`, `get_session`, `get_session_waits`, `get_blocking_sessions`, `get_long_running_sessions`
- **Plan (2):** `get_sql_plan`, `get_sql_plan_history`
- **Object (6):** `get_object_source`, `get_object_metadata`, `get_object_arguments`, `get_object_dependencies`, `get_dependency_graph`, `get_invalid_objects`
- **Storage (11):** `get_database_info`, `get_tablespace_usage`, `get_datafile_usage`, `get_segment_growth`, `get_temp_usage`, `get_undo_usage`, `get_redo_statistics`, `get_resource_usage`, `get_scheduler_jobs`, `get_scheduler_job_history`, `get_failed_jobs`

---

### 2. db-copilot (Phase 0 — Section 3.2 Foundation DONE)

**Tech stack:**
- Python 3.13, FastAPI, Uvicorn
- PostgreSQL async with SQLAlchemy 2.0 (`asyncpg`)
- Alembic async migrations
- Pydantic v2 domain models & Pydantic-Settings

**Files đã tạo:**
```
db-copilot/
├── pyproject.toml                          ← build config, deps
├── .env.example                            ← template env vars
├── .gitignore                              ← ignore __pycache__, venv, env
├── Dockerfile                              ← python:3.12-slim
├── docker-compose.yml                      ← api + postgres 16
├── alembic.ini                             ← Alembic migration config
├── README.md
├── alembic/
│   ├── env.py                              ← async migration environment
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py           ← initial PostgreSQL tables & indexes (8 tables)
├── src/db_copilot/
│   ├── main.py                             ← app entrypoint & CLI runner
│   ├── config/settings.py                  ← Pydantic Settings
│   ├── domain/
│   │   ├── enums.py                        ← Severity, IncidentCategory, EvidenceType...
│   │   └── models/
│   │       ├── evidence.py                 ← Evidence, EvidencePackage
│   │       ├── incident.py                 ← Incident, IncidentSummary, IncidentDetail
│   │       └── diagnosis.py                ← DiagnosisResult, Recommendation, Hypothesis
│   ├── db/
│   │   ├── schema.py                       ← SQLAlchemy Declarative Base & Tables
│   │   └── session.py                      ← Async engine, sessionmaker, ping
│   └── api/
│       ├── app.py                          ← FastAPI app factory with lifespan
│       ├── deps.py                         ← get_db_session dependency
│       └── routes/
│           └── health.py                   ← GET /api/v1/health (DB connectivity check)
└── tests/
    ├── conftest.py                         ← async client & db mocks
    └── unit/test_health.py                 ← 3 unit tests ✅ ALL PASSED
```

- CI/CD workflow: `.github/workflows/ci.yml` (multi-job lint & test cho cả 2 projects)

**Git commits:**
- `3.1 oracle-mcp-server` — foundation 6 tools
- `Phase 1 — all 32 MCP tools, MCP SDK 2.x, unit tests green`
- `docs: update README with all 32 tools, project structure, security model`
- `b0d69f7: feat(db-copilot): initialize db-copilot foundation (Section 3.2)`

---

### 3. Tài liệu thiết kế & Task breakdown (docs/)
```
docs/
├── 01-product/
│   ├── problem-statement.md               ✅
│   ├── brd.md                             ✅
│   └── prd.md                             ✅
├── 02-architecture/
│   ├── hld.md                             ✅
│   └── lld.md                             ✅
├── 03-technical/
│   ├── oracle-mcp-design.md               ✅
│   ├── evidence-engine-design.md          ✅
│   ├── correlation-engine-design.md       ✅
│   ├── investigation-engine-design.md     ✅
│   ├── ai-engine-design.md                ✅
│   ├── task_evidence.md                   ✅ (Task breakdown chi tiết Mục 4.2 — 8 giai đoạn)
│   ├── task_correlation.md                ✅ (Task breakdown chi tiết Phase 2 — 7 giai đoạn)
│   └── task_investigation_ai.md           ✅ (Task breakdown chi tiết Phase 3 — 9 giai đoạn)
└── 04-implementation/
    ├── implementation-plan.md             ✅ (đang tracking)
    └── test-plan.md                       ✅
```

---

## ❌ CHƯA LÀM

### Implementation Plan — theo thứ tự ưu tiên

#### Mục 4.2 — db-copilot MCP Client & Evidence Collection ← **NEXT ACTION**
> Chi tiết task: [`docs/03-technical/task_evidence.md`](file:///d:/2026/oracle_ai/docs/03-technical/task_evidence.md)

- [ ] **Giai đoạn 1: Môi trường & Dependencies** (`mcp`, `apscheduler`, `settings.py`, `.env.example`)
- [ ] **Giai đoạn 2: Tầng MCP Client Gateway** (`OracleMcpClient`, stdio client, parse JSON, audit logging)
- [ ] **Giai đoạn 3: Evidence Repository** (PostgreSQL CRUD snapshots, sql_metrics, baselines, evidence)
- [ ] **Giai đoạn 4: Evidence Normalizer** (chuẩn hóa regression, blocking, tablespace, failed jobs)
- [ ] **Giai đoạn 5: Collectors** (`SqlCollector`, `SessionCollector`, `StorageCollector`)
- [ ] **Giai đoạn 6: Baseline Engine** (lọc nhiễu > 2 stddev, tính mean/stddev/p50/p95, đánh giá reliable)
- [ ] **Giai đoạn 7: Scheduler & Lifespan** (`AsyncIOScheduler`, job 5 phút & 1 giờ, nối vào FastAPI)
- [ ] **Giai đoạn 8: Unit Tests & Hoàn thiện** (pytest xanh 100%, ruff check sạch)

---

#### Phase 2 — Health & Correlation Engine
> Chi tiết task: [`docs/03-technical/task_correlation.md`](file:///d:/2026/oracle_ai/docs/03-technical/task_correlation.md)

- [ ] **Giai đoạn 1:** `IncidentRepository` & Quản lý vòng đời incident (OPEN, INVESTIGATING, RESOLVED, Deduplication)
- [ ] **Giai đoạn 2:** 6 Detection Rules tất định (`SqlRegressionRule`, `BlockingSessionRule`, `LongRunningSessionRule`, `TablespaceThresholdRule`, `JobFailureRule`, `InvalidObjectRule`)
- [ ] **Giai đoạn 3:** `EvidenceGraph` (Node/Edge, causal chain via BFS)
- [ ] **Giai đoạn 4:** `HypothesisEngine` (Ma trận 5 giả thuyết gốc)
- [ ] **Giai đoạn 5:** `CorrelationEngine Orchestrator` (Rules -> Graph -> Hypothesis -> Incident)
- [ ] **Giai đoạn 6:** REST API cho Incidents (`GET /incidents`, `GET /incidents/{id}`, `PATCH /resolve`)
- [ ] **Giai đoạn 7:** Kiểm thử tổng hợp Phase 2

---

#### Phase 3 — AI & Investigation Engine
> Chi tiết task: [`docs/03-technical/task_investigation_ai.md`](file:///d:/2026/oracle_ai/docs/03-technical/task_investigation_ai.md)

- [ ] **Giai đoạn 1:** `LLMProvider` Interface & Adapters (Gemini, Claude, OpenAI)
- [ ] **Giai đoạn 2:** Prompt Engineering (`DIAGNOSIS_SYSTEM_PROMPT`, `REPORT_SYSTEM_PROMPT`) & `AIService` fallback
- [ ] **Giai đoạn 3:** `IntentParser` & `InvestigationPlanner`
- [ ] **Giai đoạn 4:** `InvestigationExecutor` (timeout 10s) & `SourceCodeMapper`
- [ ] **Giai đoạn 5:** `InvestigationEngine Orchestrator` (End-to-end question -> diagnosis)
- [ ] **Giai đoạn 6:** `DailyReportService` (Health score 0-100, cron 6:00 AM, Slack webhook)
- [ ] **Giai đoạn 7:** REST & WebSocket APIs (`/investigate`, streaming status, `/reports/daily`)
- [ ] **Giai đoạn 8:** Frontend Web Dashboard (React/Next.js)
- [ ] **Giai đoạn 9:** Kiểm thử E2E

---

## Constraint quan trọng cần nhớ
1. Oracle account **read-only** — không DML/DDL/EXECUTE
2. Oracle credentials **không bao giờ** được gửi cho LLM hoặc ghi log
3. Mọi query phải dùng **bind variables** — không string interpolation
4. Tech stack ưu tiên: **Python** (không phải .NET)
5. Tham chiếu: `docs/required/hld.md` và `docs/required/project_struct.md` là nguồn sự thật về architecture
