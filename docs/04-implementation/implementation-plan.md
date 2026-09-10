# Implementation Plan
# Kế Hoạch Triển Khai

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan Chiến Lược

Hệ thống được build theo **4 MVP**, mỗi MVP có deliverable cụ thể và success criteria đo lường được. Ưu tiên backend/engine trước, frontend sau.

### Hai project song song

| Project | Phase bắt đầu | Độc lập |
|---|---|---|
| `oracle-mcp-server` | Phase 0 | Deploy độc lập |
| `db-copilot` | Phase 1 | Phụ thuộc oracle-mcp-server |

---

## 2. Roadmap Tổng Thể

```
Phase 0 (1-2 tuần)
├── oracle-mcp-server: Setup, Oracle connection, 3 tools
└── db-copilot: Project setup, PostgreSQL, FastAPI skeleton

Phase 1 (2-3 tuần)
├── oracle-mcp-server: 32 tools, audit, security
└── db-copilot: MCP client, evidence collection, baselines

Phase 2 (2 tuần)
├── oracle-mcp-server: (stable)
└── db-copilot: Detection rules, incident engine, health engine

Phase 3 (1-2 tuần)
└── db-copilot: AI Daily Report, LLM integration

Phase 4 (2-3 tuần)
└── db-copilot: Investigation Engine, hypothesis engine

Phase 5 (1-2 tuần)
└── db-copilot: React UI, polish, documentation
```

**Tổng ước tính:** 9–14 tuần

---

## 3. Phase 0 — Foundation (1–2 tuần)

### 3.1 oracle-mcp-server

**Tasks:**
- [x] Khởi tạo Python project với `pyproject.toml`
- [x] Cài đặt `python-oracledb` thin mode
- [x] Implement `OracleConnectionPool` với async pool (`oracle/connection.py`)
- [x] Implement `AuditContext` context manager (`security/audit.py`)
- [x] MCP server entry point (`server.py`) — 6 tools registered
- [x] 6 tools: `get_database_info`, `get_top_sql`, `get_sql_statistics`, `get_active_sessions`, `get_blocking_sessions`, `get_long_running_sessions`
- [x] Unit tests với mock Oracle (`tests/unit/test_phase0_tools.py`)
- [x] Dockerfile
- [x] README với setup instructions + Claude Desktop / Cursor config
- [x] `.env.example`
- [x] `security/sanitizer.py` — credential masking
- [x] `models/response_models.py` — Pydantic output contracts

**Success Criteria:**
> `get_database_info` tool trả về database version và instance info từ Oracle thật.

### 3.2 db-copilot

**Tasks:**
- [x] Khởi tạo Python project với `pyproject.toml`
- [x] FastAPI app factory với lifespan
- [x] PostgreSQL async setup (asyncpg + SQLAlchemy)
- [x] Alembic migrations setup
- [x] Domain models: Evidence, Incident, DiagnosisResult
- [x] Settings với Pydantic Settings (env vars)
- [x] Health check endpoint: `GET /api/v1/health`
- [x] Docker Compose (api + postgres)
- [x] CI/CD pipeline skeleton (GitHub Actions)

**Success Criteria:**
> `GET /api/v1/health` trả về 200 với PostgreSQL connection status.

---

## 4. Phase 1 — Oracle MCP Complete (2–3 tuần)

### 4.1 oracle-mcp-server — Tất cả 32 Tools

**Week 1:**
- [x] `tools/sql.py`: `get_top_sql`, `get_sql_statistics`, `get_sql_wait_events`, `get_sql_execution_context`
- [x] `tools/ash.py`: `get_ash_sample`, `get_ash_sql_activity`
- [x] `tools/awr.py`: `get_awr_snapshot`, `get_awr_sql_stats`
- [x] `oracle/repositories/sql_repo.py` với Oracle queries
- [x] `oracle/repositories/awr_repo.py`, `ash_repo.py`

**Week 2:**
- [x] `tools/session.py`: 5 session tools (get_session, get_session_waits added)
- [x] `tools/plan.py`: `get_sql_plan`, `get_sql_plan_history`
- [x] `tools/object.py`: 6 object/code tools
- [x] `tools/storage.py`: 11 storage/job/health tools
- [x] Full audit system (`security/audit.py` + `sanitizer.py`)
- [x] Oracle permission grants script (`docs/grants.sql`)
- [x] MCP SDK 2.x migration (`MCPServer` + `@mcp.tool()` decorators)
- [x] `tests/conftest.py` — fake Oracle env for unit tests

**Week 3 (nếu cần):**
- [ ] Integration tests với Oracle test instance
- [ ] Error handling cho Oracle-specific errors (ORA-xxxxx)
- [ ] Connection retry logic
- [ ] Performance testing (mỗi tool < 5s)

**Success Criteria:**
> AI client (Cursor/Claude Desktop) có thể hỏi và nhận structured Oracle evidence từ tất cả 32 tools.

### 4.2 db-copilot — MCP Client & Evidence Collection

- [ ] `OracleMcpClient` implementation
- [ ] `SqlCollector`, `SessionCollector`, `StorageCollector`
- [ ] `EvidenceNormalizer`
- [ ] `EvidenceRepository` (PostgreSQL CRUD)
- [ ] APScheduler setup (5-minute collection)
- [ ] `BaselineEngine` (hourly recalculation)
- [ ] Database migration scripts

**Success Criteria:**
> db-copilot tự động thu thập SQL metrics mỗi 5 phút và lưu vào PostgreSQL.

---

## 5. Phase 2 — Health Engine (2 tuần)

**Tasks:**
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
- [ ] API endpoints: `GET /incidents`, `GET /incidents/{id}`
- [ ] Health score calculator
- [ ] `GET /api/v1/database/status`

**Success Criteria:**
> Hệ thống tự phát hiện SQL regression mà không cần AI. Khi inject SQL chạy chậm, incident tự động được tạo trong < 10 phút.

---

## 6. Phase 3 — AI Daily Report (1–2 tuần)

**Tasks:**
- [ ] `LLMProvider` abstract class
- [ ] `OpenAIProvider` implementation
- [ ] `DiagnosisPrompt` và `ReportPrompt`
- [ ] `AIService` với fallback logic
- [ ] `ReportService` với APScheduler (6:00 AM)
- [ ] `DailyReport` PostgreSQL table + repository
- [ ] API: `GET /reports/daily`, `GET /reports/daily/{date}`
- [ ] Slack webhook delivery (optional)
- [ ] Email delivery (optional)
- [ ] `ClaudeProvider`, `GeminiProvider` (nếu cần)

**Success Criteria:**
> Daily report tự động tạo vào 6:00 AM với structured evidence và AI-generated narrative. Mỗi incident có confidence score và recommendation.

---

## 7. Phase 4 — Investigation Copilot (2–3 tuần)

**Tasks:**
- [ ] `IntentParser` (LLM-based)
- [ ] `InvestigationPlanner` (4 intent types)
- [ ] `InvestigationExecutor` với dynamic deps
- [ ] `InvestigationContext`
- [ ] `EvidenceBuilder` từ investigation results
- [ ] API: `POST /investigate`, `GET /investigate/{id}`
- [ ] Async investigation (queue-based)
- [ ] WebSocket cho streaming results
- [ ] Source code mapping (SQL_ID → Procedure → Line)

**Success Criteria:**
> User hỏi _"Why was PROC_SETTLEMENT slow at 14:32?"_ và nhận diagnosis với evidence trong < 60 giây.

---

## 8. Phase 5 — UI & Polish (1–2 tuần)

**Tasks:**
- [ ] React app setup (Vite)
- [ ] Dashboard với health score
- [ ] Incident feed
- [ ] Investigation chat interface
- [ ] SQL detail page (plan tree, metrics chart)
- [ ] Daily report page
- [ ] Responsive layout
- [ ] Dark mode

**Success Criteria:**
> DBA có thể xem dashboard, đọc daily report và hỏi investigation question chỉ từ browser.

---

## 9. Feature Priority Matrix

| Feature | MVP Phase | Priority |
|---|---|---|
| oracle-mcp-server foundation | Phase 0 | P0 |
| Read-only Oracle security | Phase 0 | P0 |
| All 32 MCP tools | Phase 1 | P0 |
| Audit logging | Phase 1 | P0 |
| Evidence collection (5-min) | Phase 1 | P0 |
| SQL baseline engine | Phase 1 | P0 |
| SQL regression detection | Phase 2 | P0 |
| Blocking detection | Phase 2 | P0 |
| Tablespace detection | Phase 2 | P0 |
| Job failure detection | Phase 2 | P1 |
| Hypothesis engine | Phase 2 | P0 |
| Evidence store (PostgreSQL) | Phase 1 | P0 |
| LLM integration | Phase 3 | P1 |
| Daily report | Phase 3 | P1 |
| AI diagnosis | Phase 3 | P1 |
| Investigation engine | Phase 4 | P1 |
| Source code mapping | Phase 4 | P1 |
| React UI | Phase 5 | P2 |
| Git correlation | Future | P2 |
| Knowledge graph | Future | P2 |
| Autonomous remediation | **Never** | ❌ |

---

## 10. Những Thứ KHÔNG Làm (Non-goals)

| Không làm | Lý do |
|---|---|
| Tự động execute bất kỳ SQL nào lên Oracle | Vi phạm nguyên tắc Human-in-control |
| Autonomous DBA | Không phù hợp với nguyên tắc security |
| Automatic SQL tuning / index / statistics | Ngoài scope MVP |
| Multi-database support (MySQL, SQL Server) | Tập trung Oracle trước |
| Complex BI reporting | Ngoài scope |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Oracle test instance không available | Medium | Mock Oracle với pre-recorded responses |
| LLM structured output không consistent | Medium | JSON mode, retry logic, fallback to rule-engine |
| Investigation > 60s | Medium | Per-step timeout (10s), skip optional steps |
| AWS/GCP Oracle connectivity | Low | Document VPN/network requirements |
| LLM cost overrun | Low | Token counting, caching, rate limiting |

---

---

# 🇬🇧 ENGLISH SECTION

---

## 12. Strategy Overview

Build in **4 MVPs**, each with concrete deliverables and measurable success criteria. Prioritize backend/engine first, frontend last.

### Two parallel projects

| Project | Start Phase | Independent |
|---|---|---|
| `oracle-mcp-server` | Phase 0 | Deploy independently |
| `db-copilot` | Phase 1 | Depends on oracle-mcp-server |

---

## 13. Roadmap Summary

| Phase | Duration | Key Deliverables |
|---|---|---|
| Phase 0 — Foundation | 1–2 weeks | Project setup, Oracle connection, 3 tools, PostgreSQL, FastAPI skeleton |
| Phase 1 — Oracle MCP Complete | 2–3 weeks | All 32 MCP tools, audit, evidence collection, baselines |
| Phase 2 — Health Engine | 2 weeks | 6 detection rules, hypothesis engine, incident API |
| Phase 3 — AI Daily Report | 1–2 weeks | LLM integration, daily report, delivery channels |
| Phase 4 — Investigation Copilot | 2–3 weeks | Intent parsing, investigation engine, source code mapping |
| Phase 5 — UI & Polish | 1–2 weeks | React dashboard, investigation UI |

**Total Estimate: 9–14 weeks**

---

## 14. Phase Success Criteria Summary

| Phase | Success Criterion |
|---|---|
| Phase 0 | `get_database_info` returns Oracle info; `GET /health` returns 200 |
| Phase 1 | AI client can ask any of 32 tools and get structured Oracle evidence |
| Phase 2 | System auto-detects SQL regression within 10 minutes without AI |
| Phase 3 | Daily report auto-generated at 6 AM with structured evidence and AI narrative |
| Phase 4 | User asks _"Why was PROC_X slow?"_ and gets evidence-backed diagnosis in < 60s |
| Phase 5 | DBA can use dashboard, read reports, and run investigations from browser |

---

## 15. Non-goals

- Auto-execute any SQL against Oracle — violates Human-in-control
- Autonomous DBA capabilities
- Automatic SQL tuning, index creation, or statistics gathering
- Multi-database support in MVP
- Complex BI reporting
