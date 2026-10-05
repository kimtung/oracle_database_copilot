# Oracle DB Copilot — Session State

**Last Updated:** 2026-09-16 21:00 (UTC+7)
**Git Commit:** 506b827

---

## Project Completion Status

### Phase 0 — Foundation ✅ DONE
- oracle-mcp-server: 32 MCP tools (Thin mode, read-only Oracle gateway), 14/14 tests pass
- db-copilot: FastAPI + SQLAlchemy 2.0 + Alembic, 8 PostgreSQL tables, CI/CD

### Phase 1 / Section 4.2 — MCP Client & Evidence Collection ✅ DONE (commit 0ba893c)
- OracleMcpClient, EvidenceRepository, EvidenceNormalizer
- BaseCollector, SqlCollector, SessionCollector, StorageCollector
- BaselineEngine (μ±2σ outlier filtering, p50/p95)
- EvidenceScheduler (APScheduler, 5-min collection + 1-hour baseline)
- 26/26 unit tests pass

### Phase 2 — Health & Correlation Engine ✅ DONE
- IncidentRepository, 6 Deterministic Detection Rules
- EvidenceGraph (DirectedGraph, BFS causal chains)
- HypothesisEngine (5 root hypotheses, confidence scoring)
- CorrelationEngine (Rules→Graph→Hypothesis→Incident)
- REST API: GET/PATCH /api/v1/incidents
- 49/49 unit tests pass

### Phase 3 — AI & Investigation Engine ✅ DONE (commit 506b827)
- LLMProvider ABC (domain/interfaces/llm_provider.py)
- GeminiProvider, OpenAIProvider, ClaudeProvider (lazy imports)
- Diagnosis & Report prompt templates (ai/prompts/)
- AIService: primary/fallback/rule-based diagnosis with timeout
- IntentParser (regex, 5 intent types)
- InvestigationPlanner (per-intent MCP step templates + deps)
- InvestigationContext (dynamic param resolution $step_N.field)
- InvestigationExecutor (10s timeout/step, graceful optional fail)
- SourceCodeMapper (sql_id → PL/SQL fragment)
- InvestigationEngine (end-to-end orchestrator)
- DailyReportService (health score 0-100, persists to daily_reports)
- NotificationService (Slack/Teams webhook)
- REST API: POST/GET /api/v1/investigate
- WebSocket: WS /api/v1/ws/investigate/{id}
- REST API: GET /api/v1/reports/daily, /reports/daily/{date}
- Extended Settings with LLM provider config
- Extended EvidencePackage with Phase 3 LLM context fields
- **93/93 unit tests pass, ruff check clean**

---

### Phase 3.8 / Phase 5 — Frontend Web Dashboard ✅ DONE
- React 19 + TypeScript + Vite 8 + Tailwind CSS v4 + Lucide Icons in `frontend/`
- `Navbar`: 19c Thin Mode status, MCP Gateway status, live auto-refresh
- `HealthScoreGauge`: Dynamic circular SVG gauge (0-100 index, CBO & AWR sub-indices)
- `MetricsGrid`: Active Sessions, Blocking Sessions, CPU%, Tablespace%, Invalid Objects
- `IncidentFeed`: Multi-severity filters, instant search, status update, quick "Điều Tra AI" transfer
- `InvestigationChat`: Multi-step MCP timeline, AI diagnosis with confidence %, copyable SQL remediations
- `ExecutionPlanViewer`: Interactive CBO hierarchical tree highlighting Full Table Scans and cost
- `DailyReportViewer`: Executive narrative reader, date selector, print/PDF export
- `apiService`: Live REST + WebSocket support with interactive standalone fallback
- Production build: `npm run build` passed in 714ms, `oxlint` 0 warnings 0 errors
- FastAPI Backend: CORSMiddleware enabled for dev & production proxy

---

## NEXT ACTION: Deployment & Real Oracle 19c Integration Testing

When resuming:
1. Configure `.env` with actual Oracle 19c database connection strings.
2. Run end-to-end integration tests with live Oracle performance views (`V$SQL`, `V$SESSION`, `DBA_TABLESPACES`).
3. Deploy frontend & backend services via Docker Compose.


---

## Tech Stack
- Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, APScheduler
- LLM: Gemini (primary), OpenAI (fallback), Claude (optional)
- MCP protocol: stdio JSON-RPC (oracle-mcp-server subprocess)
- Tests: pytest-asyncio, aiosqlite (in-memory), all mocked
- Lint: ruff (line-length=100), all clean
