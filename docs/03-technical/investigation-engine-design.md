# Investigation Engine Design
# Thiết Kế Investigation Engine

**Project:** `db-copilot` — `investigation/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Investigation Engine là "bộ não" của hệ thống — xử lý câu hỏi tự nhiên từ người dùng và tự động thực hiện toàn bộ quy trình điều tra.

**Input:** Câu hỏi tiếng Anh từ user (vd: _"Why was PROC_SETTLEMENT slow at 14:32?"_)

**Output:** Structured `InvestigationResult` với evidence, hypotheses và diagnosis.

---

## 2. Component Overview

```
db-copilot/investigation/
│
├── planner.py    # Intent Parser + Investigation Planner
├── executor.py   # Execute investigation steps via oracle-mcp-server
└── context.py    # Investigation state (kết quả từng step)
```

---

## 3. Full Pipeline

```
User Question
      │
      ▼
┌─────────────────┐
│  Intent Parser   │
│                  │
│ Parse: type,     │
│ entities,        │
│ time_range,      │
│ focus_metric     │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Planner        │
│                  │
│ Intent →         │
│ Ordered steps    │
│ (with deps)      │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Executor       │
│                  │
│ Execute steps    │
│ via MCP calls    │
│ Dynamic deps     │
│ Timeout: 10s/call│
│ Continue on err  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Evidence Build  │
│                  │
│ Raw results →    │
│ Evidence objects │
│ Evidence graph   │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Hypothesis Eng. │
│                  │
│ Rank hypotheses  │
│ with confidence  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  AI Diagnosis    │
│                  │
│ Evidence pkg →   │
│ LLM →            │
│ Structured JSON  │
└────────┬─────────┘
         │
         ▼
   InvestigationResult
```

---

## 4. Intent Types & Parsing

### 4.1 Supported Intent Types

| IntentType | Ví dụ câu hỏi |
|---|---|
| `PROCEDURE_SLOW` | "Why was PROC_SETTLEMENT slow at 14:32?" |
| `SQL_SLOW` | "Why was SQL_ID 8f3abc slow yesterday?" |
| `SQL_TOP` | "Which SQL is slowest today?" |
| `HEALTH_CHECK` | "What issues does the database have?" |
| `BLOCKING_CHECK` | "Is there any blocking?" |
| `TABLESPACE_CHECK` | "How is the storage looking?" |
| `JOB_CHECK` | "Did any jobs fail today?" |
| `GENERAL_INCIDENT` | "What happened to the database last night?" |

### 4.2 Intent Schema

```python
@dataclass
class InvestigationIntent:
    type: IntentType
    entities: list[Entity]      # {"type": "PROCEDURE", "name": "PROC_SETTLEMENT"}
    time_range: TimeRange       # {begin: datetime, end: datetime}
    focus_metric: str | None    # "elapsed_time", "cpu", "io", "blocking"
    question_text: str          # Original question

@dataclass
class Entity:
    type: str    # "PROCEDURE", "SQL", "TABLE", "SESSION", "JOB"
    name: str
    owner: str | None = None

@dataclass
class TimeRange:
    begin: datetime
    end: datetime
    is_approximate: bool = True  # True nếu LLM suy ra từ "at 14:32"
```

### 4.3 Intent Parsing

```python
# src/db_copilot/investigation/planner.py

class IntentParser:
    """
    Dùng LLM để parse natural language thành InvestigationIntent.
    Separate LLM call, nhỏ và nhanh.
    """

    SYSTEM_PROMPT = """
    You are an Oracle Database investigation assistant.
    Parse the user's question and extract:
    - intent type (from predefined list)
    - entities (procedure names, SQL IDs, table names, job names)
    - time range (derive from "at 14:32", "yesterday", "this morning", etc.)
    - focus metric

    Return JSON only. Current time: {current_time}
    """

    async def parse(self, question: str) -> InvestigationIntent:
        response = await self.llm.complete(
            system=self.SYSTEM_PROMPT.format(current_time=datetime.utcnow()),
            user=question,
            response_format="json"
        )
        return InvestigationIntent(**json.loads(response))
```

---

## 5. Investigation Plans Per Intent Type

### 5.1 PROCEDURE_SLOW Plan

```python
def plan_procedure_slow(intent: InvestigationIntent) -> InvestigationPlan:
    proc_name = intent.entities[0].name
    t_begin = intent.time_range.begin - timedelta(minutes=15)
    t_end = intent.time_range.end + timedelta(minutes=15)

    return InvestigationPlan(steps=[
        Step("get_object_metadata",
             args={"name": proc_name, "type": "PROCEDURE", "owner": intent.entities[0].owner},
             produces="proc_metadata"),

        Step("get_ash_sql_activity",
             args={"begin_time": t_begin, "end_time": t_end},
             produces="ash_activity"),

        Step("get_sql_statistics",
             args={"sql_id": DependsOn("ash_activity", extract="top_sql_id")},
             produces="sql_stats"),

        Step("get_sql_plan_history",
             args={"sql_id": DependsOn("sql_stats", extract="sql_id"), "days": 3},
             produces="plan_history"),

        Step("get_sql_wait_events",
             args={"sql_id": DependsOn("sql_stats", extract="sql_id"), "hours": 4},
             produces="wait_events"),

        Step("get_awr_sql_stats",
             args={
                 "sql_id": DependsOn("sql_stats", extract="sql_id"),
                 "begin_snap": DependsOn("ash_activity", extract="nearest_snapshot_begin"),
                 "end_snap": DependsOn("ash_activity", extract="nearest_snapshot_end")
             },
             produces="awr_stats"),

        Step("get_blocking_sessions",
             args={},
             produces="blocking"),

        Step("get_resource_usage",
             args={},
             produces="resource"),

        Step("get_object_source",
             args={"name": proc_name, "type": "PROCEDURE",
                   "owner": DependsOn("proc_metadata", extract="owner")},
             produces="source_code",
             optional=True),  # Không fail investigation nếu không lấy được
    ])
```

### 5.2 SQL_SLOW Plan

```python
def plan_sql_slow(intent: InvestigationIntent) -> InvestigationPlan:
    sql_id = intent.entities[0].name  # SQL_ID

    return InvestigationPlan(steps=[
        Step("get_sql_statistics", args={"sql_id": sql_id}, produces="sql_stats"),
        Step("get_sql_plan_history", args={"sql_id": sql_id, "days": 7}, produces="plan_history"),
        Step("get_sql_wait_events", args={"sql_id": sql_id, "hours": 24}, produces="wait_events"),
        Step("get_awr_sql_stats", args={"sql_id": sql_id, "days": 1}, produces="awr_stats"),
        Step("get_sql_execution_context", args={"sql_id": sql_id}, produces="context"),
        Step("get_blocking_sessions", args={}, produces="blocking"),
        Step("get_resource_usage", args={}, produces="resource"),
    ])
```

### 5.3 HEALTH_CHECK Plan

```python
def plan_health_check(intent: InvestigationIntent) -> InvestigationPlan:
    return InvestigationPlan(steps=[
        Step("get_top_sql", args={"metric": "elapsed_time", "limit": 10, "hours": 24}),
        Step("get_blocking_sessions", args={}),
        Step("get_tablespace_usage", args={}),
        Step("get_failed_jobs", args={"hours": 24}),
        Step("get_invalid_objects", args={}),
        Step("get_resource_usage", args={}),
        Step("get_long_running_sessions", args={"min_minutes": 30}),
    ])
```

---

## 6. Investigation Executor

```python
# src/db_copilot/investigation/executor.py

class InvestigationExecutor:

    async def execute(self, question: str) -> InvestigationResult:
        # 1. Parse intent
        intent = await self.intent_parser.parse(question)

        # 2. Create plan
        plan = self.planner.create_plan(intent)

        # 3. Execute steps
        context = InvestigationContext()

        for step in plan.steps:
            try:
                # Resolve dynamic dependencies
                resolved_args = self._resolve_args(step.args, context)

                # Call oracle-mcp-server
                result = await asyncio.wait_for(
                    self.mcp_client.call_tool(step.tool, resolved_args),
                    timeout=10.0  # 10 second timeout per tool
                )

                context.add_result(step.produces, result)

            except asyncio.TimeoutError:
                context.add_error(step.produces, "timeout")
                if not step.optional:
                    # Log warning but continue
                    logger.warning(f"Step {step.tool} timed out")

            except Exception as e:
                context.add_error(step.produces, str(e))
                if not step.optional:
                    logger.error(f"Step {step.tool} failed: {e}")

        # 4. Build evidence
        evidence_list = self.evidence_builder.build_from_context(context, intent)
        graph = self._build_evidence_graph(evidence_list, context)

        # 5. Generate hypotheses
        hypotheses = self.correlation_engine.rank_hypotheses(evidence_list)

        # 6. AI diagnosis
        package = EvidencePackage(
            question=question,
            intent=intent,
            evidence=evidence_list,
            hypotheses=hypotheses,
            graph=graph,
            context_data=context.to_dict()
        )
        diagnosis = await self.ai_service.diagnose(package)

        return InvestigationResult(
            id=uuid4(),
            question=question,
            intent=intent,
            evidence=evidence_list,
            hypotheses=hypotheses,
            diagnosis=diagnosis,
            duration_seconds=context.elapsed_seconds
        )

    def _resolve_args(self, args: dict, context: InvestigationContext) -> dict:
        """Resolve DependsOn references to actual values from previous step results."""
        resolved = {}
        for key, value in args.items():
            if isinstance(value, DependsOn):
                resolved[key] = context.extract(value.source, value.path)
            else:
                resolved[key] = value
        return resolved
```

---

## 7. Investigation Context

```python
# src/db_copilot/investigation/context.py

class InvestigationContext:
    """
    Holds all results from investigation steps.
    Allows dynamic dependency resolution.
    """

    def __init__(self):
        self.results: dict[str, Any] = {}
        self.errors: dict[str, str] = {}
        self.start_time = time.time()

    def add_result(self, key: str, value: Any):
        self.results[key] = value

    def add_error(self, key: str, error: str):
        self.errors[key] = error

    def extract(self, source: str, path: str) -> Any:
        """
        Extract value from a previous step result.
        path: "top_sql_id" → result["top_sql"][0]["sql_id"]
        """
        data = self.results.get(source)
        if data is None:
            return None
        return self._get_by_path(data, path)

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def to_dict(self) -> dict:
        return {"results": self.results, "errors": self.errors}
```

---

## 8. InvestigationResult Schema

```python
@dataclass
class InvestigationResult:
    id: UUID
    question: str
    intent: InvestigationIntent
    evidence: list[Evidence]
    hypotheses: list[Hypothesis]
    diagnosis: DiagnosisResult
    duration_seconds: float
    created_at: datetime = field(default_factory=datetime.utcnow)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 9. Overview

Investigation Engine is the "brain" of the system — processes natural language questions and automatically performs the full investigation workflow.

**Input:** Natural language question (e.g., _"Why was PROC_SETTLEMENT slow at 14:32?"_)

**Output:** Structured `InvestigationResult` with evidence, hypotheses, and diagnosis.

---

## 10. Pipeline Summary

1. **Intent Parser** (LLM): Parse natural language → structured intent (type, entities, time range, metric)
2. **Planner**: Intent → Ordered investigation steps with dynamic dependencies
3. **Executor**: Execute steps via oracle-mcp-server MCP calls (10s timeout, continue on error)
4. **Evidence Builder**: Raw results → typed Evidence objects + Evidence graph
5. **Hypothesis Engine**: Rank hypotheses by confidence (deterministic scoring)
6. **AI Diagnosis**: EvidencePackage → LLM → Structured DiagnosisResult

---

## 11. Investigation Plans

| Intent Type | Steps Count | Key MCP Tools Used |
|---|---|---|
| `PROCEDURE_SLOW` | 9 steps | ash_activity, sql_statistics, plan_history, wait_events, awr_stats, blocking, resource, object_source |
| `SQL_SLOW` | 7 steps | sql_statistics, plan_history, wait_events, awr_stats, execution_context, blocking, resource |
| `HEALTH_CHECK` | 7 steps | top_sql, blocking, tablespace, failed_jobs, invalid_objects, resource, long_running |

---

## 12. Dynamic Dependencies

Steps can depend on previous step results:

```python
Step("get_sql_statistics",
     args={"sql_id": DependsOn("ash_activity", extract="top_sql_id")})
```

This means: _"The sql_id argument comes from the result of the 'ash_activity' step, extracted via the 'top_sql_id' path."_

If a dependency fails, the dependent step is skipped (for optional steps) or logs a warning and continues.

---

## 13. Performance Target

- Total investigation time: **< 60 seconds**
- Per MCP tool call timeout: **10 seconds**
- Continue on individual step failures — partial results are still valuable
- Minimum viable result: Can provide diagnosis even with incomplete evidence (lower confidence)
