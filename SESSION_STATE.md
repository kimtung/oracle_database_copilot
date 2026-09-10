# 📌 SESSION STATE — Oracle DB Copilot
> Cập nhật lần cuối: 2026-09-10 15:35 (GMT+7)

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

### oracle-mcp-server (Phase 0 + Phase 1 DONE)

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
│   └── grants.sql                          ← Oracle DBA script tạo read-only account
├── src/oracle_mcp/
│   ├── server.py                           ← entry point, 32 tools registered
│   ├── config/settings.py                  ← Pydantic Settings (lazy)
│   ├── oracle/
│   │   ├── connection.py                   ← async pool
│   │   ├── queries/
│   │   │   ├── sql_queries.py              ← V$SQL, V$SESSION queries
│   │   │   ├── ash_queries.py              ← V$ASH, DBA_HIST_ASH queries
│   │   │   ├── awr_queries.py              ← DBA_HIST_SNAPSHOT, DBA_HIST_SQLSTAT
│   │   │   ├── object_queries.py           ← V$SQL_PLAN, ALL_SOURCE, ALL_DEPS
│   │   │   └── storage_queries.py          ← DBA_TABLESPACES, V$LOG, DBA_SCHEDULER
│   │   └── repositories/
│   │       ├── base.py                     ← _fetchall / _fetchone
│   │       ├── sql_repo.py                 ← SQL + session repos
│   │       ├── ash_repo.py
│   │       ├── awr_repo.py
│   │       ├── object_repo.py
│   │       └── storage_repo.py
│   ├── tools/
│   │   ├── sql.py      ← get_top_sql, get_sql_statistics, get_sql_wait_events, get_sql_execution_context
│   │   ├── ash.py      ← get_ash_sample, get_ash_sql_activity
│   │   ├── awr.py      ← get_awr_snapshot, get_awr_sql_stats
│   │   ├── session.py  ← get_active_sessions, get_session, get_session_waits,
│   │   │                  get_blocking_sessions, get_long_running_sessions
│   │   ├── plan.py     ← get_sql_plan, get_sql_plan_history
│   │   ├── object.py   ← get_object_source, get_object_metadata, get_object_arguments,
│   │   │                  get_object_dependencies, get_dependency_graph, get_invalid_objects
│   │   └── storage.py  ← get_database_info, get_tablespace_usage, get_datafile_usage,
│   │                      get_segment_growth, get_temp_usage, get_undo_usage,
│   │                      get_redo_statistics, get_resource_usage,
│   │                      get_scheduler_jobs, get_scheduler_job_history, get_failed_jobs
│   ├── models/
│   │   └── response_models.py              ← Pydantic output schemas
│   └── security/
│       ├── audit.py                        ← audit_context: JSON log mọi tool call
│       └── sanitizer.py                    ← mask credentials trong logs
└── tests/
    ├── conftest.py                         ← fake Oracle env, no real DB needed
    └── unit/test_phase0_tools.py           ← 14 tests ✅ ALL PASSED
```

**32 tools đã implement:**

| Group | Tools |
|---|---|
| SQL (4) | get_top_sql, get_sql_statistics, get_sql_wait_events, get_sql_execution_context |
| ASH (2) | get_ash_sample, get_ash_sql_activity |
| AWR (2) | get_awr_snapshot, get_awr_sql_stats |
| Session (5) | get_active_sessions, get_session, get_session_waits, get_blocking_sessions, get_long_running_sessions |
| Plan (2) | get_sql_plan, get_sql_plan_history |
| Object (6) | get_object_source, get_object_metadata, get_object_arguments, get_object_dependencies, get_dependency_graph, get_invalid_objects |
| Storage (11) | get_database_info, get_tablespace_usage, get_datafile_usage, get_segment_growth, get_temp_usage, get_undo_usage, get_redo_statistics, get_resource_usage, get_scheduler_jobs, get_scheduler_job_history, get_failed_jobs |

**Git commits:**
- `3.1 oracle-mcp-server` — foundation 6 tools
- `Phase 1 — all 32 MCP tools, MCP SDK 2.x, unit tests green`
- `docs: update README with all 32 tools, project structure, security model`

### db-copilot (Phase 0 — Section 3.2 DONE)

**Tech stack:**
- Python 3.13, FastAPI, Uvicorn
- PostgreSQL async with SQLAlchemy 2.0 (asyncpg)
- Alembic async migrations
- Pydantic v2 domain models & Pydantic-Settings

**Files đã tạo:**
```
db-copilot/
├── pyproject.toml                          ← build config, deps
├── .env.example                            ← template env vars
├── Dockerfile                              ← python:3.12-slim
├── docker-compose.yml                      ← api + postgres
├── alembic.ini                             ← Alembic migration config
├── README.md
├── alembic/
│   ├── env.py                              ← async migration environment
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py           ← initial PostgreSQL tables & indexes
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

### Tài liệu (docs/)
```
docs/
├── 01-product/
│   ├── problem-statement.md   ✅
│   ├── brd.md                 ✅
│   └── prd.md                 ✅
├── 02-architecture/
│   ├── hld.md                 ✅
│   └── lld.md                 ✅
├── 03-technical/
│   ├── oracle-mcp-design.md   ✅
│   ├── evidence-engine-design.md ✅
│   ├── correlation-engine-design.md ✅
│   ├── investigation-engine-design.md ✅
│   └── ai-engine-design.md    ✅
└── 04-implementation/
    ├── implementation-plan.md ✅ (đang tracking)
    └── test-plan.md           ✅
```

---

## ❌ CHƯA LÀM

### Implementation Plan — theo thứ tự ưu tiên

#### Mục 4.2 — db-copilot MCP Client & Evidence Collection ← **NEXT ACTION**
- [ ] `OracleMcpClient` — gọi oracle-mcp-server qua MCP protocol
- [ ] `SqlCollector`, `SessionCollector`, `StorageCollector`
- [ ] `EvidenceNormalizer`
- [ ] `EvidenceRepository` (PostgreSQL CRUD)
- [ ] APScheduler setup (5-minute collection)
- [ ] `BaselineEngine` (hourly recalculation)
- [ ] Database migration scripts

---

#### Phase 2 — Health / Correlation Engine
- [ ] `SqlRegressionRule`
- [ ] `BlockingSessionRule`
- [ ] `TablespaceThresholdRule`
- [ ] `JobFailureRule`
- [ ] `LongRunningSessionRule`
- [ ] `InvalidObjectRule`
- [ ] `CorrelationEngine` orchestrator
- [ ] `HypothesisEngine` (5 hypothesis definitions)
- [ ] `EvidenceGraph` builder
- [ ] `IncidentRepository` (PostgreSQL)

---

#### Phase 3 — AI Investigation Engine
- [ ] `InvestigationEngine` (orchestrates all engines)
- [ ] Gemini/Claude LLM integration
- [ ] `DiagnosisReport` generation
- [ ] Chat API endpoints
- [ ] Frontend (React/Next.js)

---

## Constraint quan trọng cần nhớ
1. Oracle account **read-only** — không DML/DDL/EXECUTE
2. Oracle credentials **không bao giờ** được gửi cho LLM hoặc ghi log
3. Mọi query phải dùng **bind variables** — không string interpolation
4. Tech stack ưu tiên: **Python** (không phải .NET)
5. Tham chiếu: `docs/required/hld.md` và `docs/required/project_struct.md` là nguồn sự thật về architecture
