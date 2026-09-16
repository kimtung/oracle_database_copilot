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

## NEXT ACTION: Phase 3.8 — Frontend Web Dashboard

When resuming, implement:
- `frontend/` directory with React/Next.js + TypeScript + TailwindCSS
- Health Score Dashboard
- Investigation Copilot Chat UI (calls POST /api/v1/investigate)
- Daily Report Viewer
- WebSocket real-time progress streaming

OR: Deploy & integration testing with real Oracle instance

---

## Tech Stack
- Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, APScheduler
- LLM: Gemini (primary), OpenAI (fallback), Claude (optional)
- MCP protocol: stdio JSON-RPC (oracle-mcp-server subprocess)
- Tests: pytest-asyncio, aiosqlite (in-memory), all mocked
- Lint: ruff (line-length=100), all clean
