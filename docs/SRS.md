# SRS — Software Requirements Specification
# Đặc Tả Yêu Cầu Phần Mềm

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Trạng thái / Status:** Draft  
**Ngày / Date:** 2026-09-08

---

> 🇻🇳 **Phần tiếng Việt** — Sections 1–15  
> 🇬🇧 **English Section** — Sections 16–30

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Phạm Vi Hệ Thống (System Scope)

SRS này mô tả đặc tả chi tiết phần mềm cho DB Copilot MVP, bao gồm:

- Oracle MCP Server (Evidence Gateway)
- Health Engine (Detection rules)
- Investigation Engine (AI investigation pipeline)
- Evidence Store (PostgreSQL)
- AI Diagnosis Service
- FastAPI REST API

**Không bao gồm:**
- Frontend React (xem PRD.md cho UI specs)
- Infrastructure provisioning chi tiết
- Oracle Database administration

---

## 2. Actors & System Context

### 2.1 Human Actors

| Actor | Mô tả |
|---|---|
| **DBA** | Người dùng chính, nhận report và điều tra sự cố |
| **Database Developer** | Điều tra SQL/procedure performance |
| **Backend Developer** | Tìm hiểu vấn đề DB ảnh hưởng code |
| **System Administrator** | Cấu hình và vận hành hệ thống |

### 2.2 System Actors

| System Actor | Mô tả |
|---|---|
| **Oracle Database** | Nguồn dữ liệu duy nhất, chỉ đọc |
| **LLM Provider** | OpenAI / Claude / Gemini — nhận evidence, trả về diagnosis |
| **PostgreSQL** | Evidence Store — lưu historical data |
| **MCP Client** | AI agent hoặc CLI gọi MCP tools |

---

## 3. MCP Tool Catalog Đầy Đủ

### Group 1 — SQL Tools

| Tool | Input | Output |
|---|---|---|
| `get_top_sql` | `metric: str, limit: int, hours: int` | `List[SqlSummary]` |
| `get_sql_statistics` | `sql_id: str` | `SqlStatistics` |
| `get_sql_plan` | `sql_id: str` | `ExecutionPlan` |
| `get_sql_plan_history` | `sql_id: str, days: int` | `List[PlanHistory]` |
| `get_sql_wait_events` | `sql_id: str, hours: int` | `List[WaitEvent]` |
| `get_sql_execution_context` | `sql_id: str` | `ExecutionContext` |

### Group 2 — Session Tools

| Tool | Input | Output |
|---|---|---|
| `get_active_sessions` | `min_elapsed_sec: int` | `List[Session]` |
| `get_session` | `session_id: int, serial: int` | `SessionDetail` |
| `get_session_waits` | `session_id: int` | `List[SessionWait]` |
| `get_blocking_sessions` | _(none)_ | `List[BlockingChain]` |
| `get_long_running_sessions` | `min_minutes: int` | `List[Session]` |

### Group 3 — AWR/ASH Tools

| Tool | Input | Output |
|---|---|---|
| `get_awr_snapshot` | `hours: int` | `List[AwrSnapshot]` |
| `get_awr_sql_stats` | `sql_id: str, begin_snap: int, end_snap: int` | `AwrSqlStats` |
| `get_awr_sql_plan` | `sql_id: str, plan_hash: int` | `ExecutionPlan` |
| `get_ash_sample` | `begin_time: datetime, end_time: datetime` | `List[AshSample]` |
| `get_ash_sql_activity` | `sql_id: str, begin_time: datetime, end_time: datetime` | `AshActivity` |

### Group 4 — Storage Tools

| Tool | Input | Output |
|---|---|---|
| `get_tablespace_usage` | _(none)_ | `List[TablespaceUsage]` |
| `get_datafile_usage` | `tablespace_name: str` | `List[DatafileUsage]` |
| `get_segment_growth` | `owner: str, segment_name: str, days: int` | `SegmentGrowth` |
| `get_temp_usage` | _(none)_ | `TempUsage` |
| `get_undo_usage` | _(none)_ | `UndoUsage` |

### Group 5 — Job Tools

| Tool | Input | Output |
|---|---|---|
| `get_scheduler_job_status` | _(none)_ | `List[JobStatus]` |
| `get_scheduler_job_history` | `job_name: str, days: int` | `List[JobRun]` |
| `get_running_jobs` | _(none)_ | `List[JobRun]` |
| `get_failed_jobs` | `hours: int` | `List[JobRun]` |

### Group 6 — Database Health Tools

| Tool | Input | Output |
|---|---|---|
| `get_database_parameters` | `filter: str` | `List[DbParameter]` |
| `get_instance_status` | _(none)_ | `InstanceStatus` |
| `get_resource_usage` | _(none)_ | `ResourceUsage` |
| `get_redo_statistics` | `hours: int` | `RedoStatistics` |
| `get_alert_events` | `hours: int` | `List[AlertEvent]` |
| `get_invalid_objects` | _(none)_ | `List[InvalidObject]` |

### Group 7 — Code Intelligence Tools

| Tool | Input | Output |
|---|---|---|
| `get_object_source` | `owner: str, name: str, type: str` | `ObjectSource` |
| `get_procedure_source` | `owner: str, name: str` | `ObjectSource` |
| `get_function_source` | `owner: str, name: str` | `ObjectSource` |
| `get_package_spec` | `owner: str, name: str` | `ObjectSource` |
| `get_package_body` | `owner: str, name: str` | `ObjectSource` |
| `get_object_metadata` | `owner: str, name: str, type: str` | `ObjectMetadata` |
| `get_object_arguments` | `owner: str, name: str` | `List[Argument]` |
| `get_object_dependencies` | `owner: str, name: str, type: str` | `List[Dependency]` |
| `get_dependency_graph` | `owner: str, name: str, type: str, depth: int` | `DependencyGraph` |

---

## 4. MCP Tool Contracts Chi Tiết

### 4.1 get_sql_statistics

**Input:**
```json
{
  "sql_id": "8f3abc"
}
```

**Output:**
```json
{
  "sql_id": "8f3abc",
  "sql_text_fragment": "SELECT * FROM ACCOUNT_POSITION WHERE...",
  "executions": 12450,
  "elapsed_time_ms": 52300000,
  "cpu_time_ms": 21300000,
  "buffer_gets": 182000000,
  "disk_reads": 9300000,
  "rows_processed": 4200000,
  "last_active_time": "2026-09-08T14:32:00Z",
  "plan_hash_value": 98237412,
  "module": "PROC_SETTLEMENT",
  "action": "UPDATE_PHASE"
}
```

### 4.2 get_object_source

**Input:**
```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE"
}
```

**Output:**
```json
{
  "owner": "APP",
  "object_name": "PROC_SETTLEMENT",
  "object_type": "PROCEDURE",
  "status": "VALID",
  "last_ddl_time": "2026-09-01T10:00:00Z",
  "source_hash": "sha256:abc123...",
  "source_lines": 247,
  "source": "CREATE OR REPLACE PROCEDURE...",
  "sql_statements": [
    {"line": 247, "sql_text": "UPDATE ACCOUNT_POSITION ...", "type": "UPDATE"}
  ],
  "dependencies": [
    {"owner": "APP", "name": "ACCOUNT_POSITION", "type": "TABLE"},
    {"owner": "APP", "name": "PROC_CALCULATE", "type": "PROCEDURE"}
  ]
}
```

### 4.3 get_blocking_sessions

**Input:** _(none)_

**Output:**
```json
{
  "blocking_chains": [
    {
      "blocker": {
        "session_id": 142,
        "serial": 1023,
        "user": "APP",
        "sql_id": "abc123",
        "wait_event": "enq: TX - row lock contention",
        "elapsed_seconds": 423
      },
      "blocked": [
        {
          "session_id": 156,
          "serial": 2011,
          "user": "APP",
          "sql_id": "def456"
        }
      ]
    }
  ],
  "total_blocked": 1,
  "max_wait_seconds": 423
}
```

---

## 5. Evidence Model

### 5.1 Evidence Schema

```python
@dataclass
class Evidence:
    id: str                          # UUID
    incident_id: str                 # FK to incident
    type: EvidenceType               # Enum
    source: str                      # "DBA_HIST_SQLSTAT", "V$SESSION", etc.
    timestamp: datetime
    entity_type: str                 # "SQL", "SESSION", "OBJECT", etc.
    entity_id: str                   # sql_id, session_id, object_name
    data: dict                       # Raw evidence data
    severity: Severity               # HIGH, MEDIUM, LOW, INFO
    supports_hypothesis: list[str]   # List of hypothesis IDs this supports
```

### 5.2 Evidence Types

| Type | Nguồn Oracle | Mô tả |
|---|---|---|
| `sql_plan_change` | `DBA_HIST_SQLSTAT` | Execution plan thay đổi |
| `sql_regression` | `DBA_HIST_SQLSTAT` + `V$SQL` | SQL elapsed time tăng đột biến |
| `cardinality_mismatch` | `V$SQL_PLAN_STATISTICS_ALL` | Estimated vs actual rows lệch lớn |
| `high_physical_reads` | `DBA_HIST_SQLSTAT` | Disk reads tăng |
| `stale_statistics` | `DBA_TAB_STATISTICS` | Statistics quá cũ |
| `blocking_session` | `V$SESSION` | Session bị block |
| `tablespace_threshold` | `DBA_DATA_FILES` + `DBA_FREE_SPACE` | Tablespace vượt ngưỡng |
| `job_failure` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | Scheduler job thất bại |
| `wait_event_anomaly` | `V$SESSION_WAIT` + `ASH` | Wait event bất thường |
| `long_running_session` | `V$SESSION` | Session chạy quá lâu |

### 5.3 Evidence Graph

```
PROC_SETTLEMENT
      |
      | executes [via ASH MODULE]
      ↓
SQL_ID 8f3abc
      |
      | plan changed [DBA_HIST_SQLSTAT]
      ↓
PLAN 98237412
      |
      | accesses [from plan operations]
      ↓
ACCOUNT_POSITION (TABLE)
      |
      | statistics stale [DBA_TAB_STATISTICS]
      ↓
LAST_ANALYZED: 18 days ago
```

---

## 6. Detection Engine (Deterministic Rules)

Detection engine chạy **trước AI**, dùng rule-based logic:

### 6.1 Rule Specifications

```python
class SqlRegressionRule:
    """
    Trigger: current_elapsed > historical_avg * multiplier
    Default multiplier: 3.0
    Baseline: 7-day rolling average, same hour-of-day bucket
    Minimum executions: 10 (tránh false positive với SQL ít chạy)
    """

class TablespaceThresholdRule:
    """
    WARNING: usage_pct > 80
    CRITICAL: usage_pct > 90
    Include growth trend: bytes_per_day (linear regression trên 7 ngày)
    Include estimated_days_until_full
    """

class BlockingSessionRule:
    """
    Trigger: blocking_chain detected (V$SESSION.BLOCKING_SESSION IS NOT NULL)
    Immediate severity: HIGH
    Include full chain: blocker → blocked sessions
    Track duration: seconds since first detected
    """

class JobFailureRule:
    """
    Trigger: DBA_SCHEDULER_JOB_RUN_DETAILS.STATUS = 'FAILED'
    Severity: based on job priority config
    Include: error_message, last_successful_run
    """

class LongRunningSessionRule:
    """
    Trigger: V$SESSION.LAST_CALL_ET > threshold_seconds
    Default threshold: 3600 (1 hour)
    Configurable per schema/user
    """

class InvalidObjectRule:
    """
    Trigger: DBA_OBJECTS.STATUS = 'INVALID'
    Collect: object_name, object_type, owner, last_ddl_time
    """
```

### 6.2 Rule Output Schema

```python
@dataclass
class Incident:
    id: str
    detected_at: datetime
    severity: Severity        # CRITICAL, HIGH, MEDIUM, LOW
    category: IncidentCategory
    title: str
    description: str
    evidence: list[Evidence]
    affected_entities: list[Entity]
    status: IncidentStatus    # OPEN, INVESTIGATING, RESOLVED
    auto_resolved: bool       # True nếu tự hết mà không có action
```

---

## 7. Investigation Engine Pipeline

### 7.1 Intent Parser

**Input:** Natural language question

**Output:**
```python
@dataclass
class InvestigationIntent:
    type: IntentType          # PROCEDURE_SLOW, SQL_SLOW, HEALTH_CHECK, etc.
    entities: list[Entity]    # {type: "PROCEDURE", name: "PROC_SETTLEMENT"}
    time_range: TimeRange     # {begin: datetime, end: datetime}
    focus_metric: str | None  # "elapsed_time", "cpu", "io"
    question_text: str        # Original question
```

**Ví dụ:**
```
Input: "Why was PROC_SETTLEMENT slow at 14:32?"

Output:
{
  "type": "PROCEDURE_SLOW",
  "entities": [{"type": "PROCEDURE", "name": "PROC_SETTLEMENT"}],
  "time_range": {"begin": "2026-09-08T14:20:00", "end": "2026-09-08T14:45:00"},
  "focus_metric": "elapsed_time"
}
```

### 7.2 Investigation Planner

**Input:** `InvestigationIntent`

**Output:** Ordered `List[InvestigationStep]`

**Ví dụ plan cho PROCEDURE_SLOW:**
```python
steps = [
    InvestigationStep("get_object_metadata", {"name": "PROC_SETTLEMENT", "type": "PROCEDURE"}),
    InvestigationStep("get_ash_sql_activity", {"begin": t_minus_15, "end": t_plus_15}),
    InvestigationStep("get_sql_statistics", {"sql_id": "<from_ash>"}),
    InvestigationStep("get_sql_plan_history", {"sql_id": "<from_ash>"}),
    InvestigationStep("get_sql_wait_events", {"sql_id": "<from_ash>"}),
    InvestigationStep("get_blocking_sessions", {}),
    InvestigationStep("get_resource_usage", {}),
    InvestigationStep("get_awr_sql_stats", {"sql_id": "<from_ash>"}),
    InvestigationStep("get_object_source", {"name": "PROC_SETTLEMENT"}),
]
```

### 7.3 Evidence Collector

- Execute từng step theo thứ tự
- Một số steps phụ thuộc output của step trước (dynamic dependency)
- Timeout mỗi MCP call: 10 giây
- Continue on error (log lỗi, không dừng investigation)

### 7.4 Correlation Engine

**Rules:**

```python
def correlate(evidence_list: list[Evidence]) -> CorrelationGraph:
    """
    1. Group evidence by entity (SQL_ID, session, object)
    2. Build temporal correlation (events near same timestamp)
    3. Build causal graph (plan change → physical reads increase)
    4. Assign edge weights based on temporal proximity + causal likelihood
    """
```

### 7.5 Hypothesis Engine

**Input:** `CorrelationGraph`

**Output:** `List[Hypothesis]` sorted by confidence

```python
HYPOTHESIS_RULES = [
    {
        "name": "Statistics Issue",
        "evidence_required": ["stale_statistics", "cardinality_mismatch"],
        "evidence_supporting": ["sql_regression", "high_physical_reads"],
        "base_confidence": 0.7
    },
    {
        "name": "Execution Plan Regression",
        "evidence_required": ["sql_plan_change"],
        "evidence_supporting": ["sql_regression", "high_physical_reads", "cardinality_mismatch"],
        "base_confidence": 0.65
    },
    {
        "name": "IO Contention",
        "evidence_required": ["wait_event_anomaly"],  # db file sequential read
        "evidence_supporting": ["high_physical_reads"],
        "base_confidence": 0.5
    },
    {
        "name": "Blocking",
        "evidence_required": ["blocking_session"],
        "base_confidence": 0.9
    }
]
```

---

## 8. AI Diagnosis Service

### 8.1 LLM Provider Abstraction

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def diagnose(self, evidence_package: EvidencePackage) -> DiagnosisResult:
        pass

class OpenAIProvider(LLMProvider): ...
class ClaudeProvider(LLMProvider): ...
class GeminiProvider(LLMProvider): ...
```

### 8.2 Evidence Package Schema

```python
@dataclass
class EvidencePackage:
    question: str
    intent: InvestigationIntent
    hypotheses: list[Hypothesis]     # Pre-ranked hypotheses
    evidence: list[Evidence]          # All collected evidence
    correlation_graph: CorrelationGraph
    context: dict                     # DB name, timestamp, etc.
```

### 8.3 Structured LLM Output

LLM **phải** trả về structured JSON:

```json
{
  "diagnosis": "Execution plan regression for SQL_ID 8f3abc caused by stale statistics",
  "confidence": 0.91,
  "primary_cause": "Statistics issue → Cardinality mismatch → Bad plan",
  "evidence_used": [
    "plan_hash_changed_from_18473291_to_98237412",
    "physical_reads_increased_920pct",
    "cardinality_estimated_120_actual_4320",
    "statistics_last_updated_18_days_ago"
  ],
  "evidence_against": [
    "no_blocking_detected",
    "cpu_remained_normal"
  ],
  "recommendations": [
    {
      "action": "Gather statistics for ACCOUNT_POSITION",
      "sql": "EXEC DBMS_STATS.GATHER_TABLE_STATS('APP', 'ACCOUNT_POSITION');",
      "priority": "HIGH",
      "note": "Do NOT execute automatically. DBA must review and execute manually."
    }
  ],
  "confidence_explanation": "Strong evidence: plan change coincides with execution spike. Supporting: stale statistics with 36x cardinality mismatch. Contradicting: CPU normal (rules out resource saturation)."
}
```

---

## 9. Evidence Store Schema (PostgreSQL)

```sql
-- Database instances being monitored
CREATE TABLE database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    host VARCHAR(256) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    version VARCHAR(32),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Periodic health snapshots
CREATE TABLE snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    captured_at TIMESTAMPTZ NOT NULL,
    active_sessions INT,
    blocking_sessions INT,
    cpu_pct DECIMAL(5,2),
    health_score INT,
    raw_data JSONB
);

-- SQL performance metrics per snapshot
CREATE TABLE sql_metric (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    snapshot_id UUID REFERENCES snapshot(id),
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

-- Execution plan history
CREATE TABLE sql_plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    sql_id VARCHAR(13) NOT NULL,
    plan_hash_value BIGINT NOT NULL,
    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,
    plan_json JSONB,
    UNIQUE(database_id, sql_id, plan_hash_value)
);

-- Wait event samples
CREATE TABLE wait_event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    captured_at TIMESTAMPTZ NOT NULL,
    event_name VARCHAR(64),
    total_waits BIGINT,
    time_waited_ms BIGINT,
    sql_id VARCHAR(13)
);

-- Detected anomalies
CREATE TABLE anomaly (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    detected_at TIMESTAMPTZ NOT NULL,
    anomaly_type VARCHAR(64),
    entity_type VARCHAR(32),
    entity_id VARCHAR(128),
    severity VARCHAR(16),
    data JSONB
);

-- Raised incidents
CREATE TABLE incident (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID REFERENCES database(id),
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    severity VARCHAR(16),
    category VARCHAR(64),
    title TEXT,
    description TEXT,
    status VARCHAR(32) DEFAULT 'OPEN',
    diagnosis JSONB
);

-- Evidence per incident
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incident(id),
    type VARCHAR(64),
    source VARCHAR(128),
    timestamp TIMESTAMPTZ,
    entity_type VARCHAR(32),
    entity_id VARCHAR(128),
    severity VARCHAR(16),
    data JSONB
);

-- MCP audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(128),
    database_id UUID REFERENCES database(id),
    tool_name VARCHAR(128) NOT NULL,
    input_args JSONB,
    duration_ms INT,
    rows_returned INT,
    status VARCHAR(16),
    error_message TEXT
);
```

---

## 10. Baseline Engine Specification

### 10.1 Baseline Dimensions

| Dimension | Mô tả |
|---|---|
| `hour_of_day` | Baseline theo giờ trong ngày (0-23) |
| `day_of_week` | Baseline theo ngày trong tuần (0-6) |
| `is_business_day` | Phân biệt ngày làm việc vs ngày nghỉ |

### 10.2 Baseline Calculation

```python
def calculate_baseline(sql_id: str, hour: int, dow: int) -> SqlBaseline:
    """
    Lấy 7 ngày dữ liệu, cùng hour/dow bucket
    Tính: mean, stddev, p50, p95
    Outlier removal: loại bỏ points > 2 stddev
    Minimum data points: 5 (nếu ít hơn, không có baseline)
    """
```

### 10.3 Baseline Schema

```python
@dataclass
class SqlBaseline:
    sql_id: str
    hour_of_day: int
    day_of_week: int
    sample_count: int
    mean_elapsed_ms: float
    stddev_elapsed_ms: float
    p50_elapsed_ms: float
    p95_elapsed_ms: float
    calculated_at: datetime
    is_reliable: bool   # False nếu sample_count < 5
```

---

## 11. Source Code Mapping Specification

### 11.1 Mapping Algorithm

```
1. Lấy SQL_ID execution context từ V$SQL (MODULE, ACTION)
2. Nếu MODULE = package/procedure name → direct mapping
3. Nếu không → tìm trong ALL_SOURCE các SQL statements khớp
4. Parse source code, extract SQL statements với line numbers
5. Match SQL statement text với SQL_ID text (normalized)
6. Assign mapping state: exact / inferred / unavailable
```

### 11.2 Source Parsing

```python
def extract_sql_from_source(source: str) -> list[SqlStatement]:
    """
    Extract các SQL statements từ PL/SQL source
    Bao gồm: SELECT, INSERT, UPDATE, DELETE, MERGE, EXECUTE IMMEDIATE
    Trả về: [(line_number, sql_type, sql_text_normalized)]
    Không gửi toàn bộ source cho LLM
    Chỉ gửi relevant fragment (±20 lines quanh matching line)
    """
```

### 11.3 Historical Source Code Limitation

```
QUAN TRỌNG: LAST_DDL_TIME không đủ để kết luận code change gây regression.

Cần thêm:
- Git history (future)
- Deployment metadata (future)
- Source snapshot tại thời điểm sự cố (future)

MVP: Chỉ đọc source code hiện tại + LAST_DDL_TIME
MVP: Ghi rõ mapping_state trong mọi output
MVP: Không kết luận "code change caused this" khi thiếu deployment data
```

---

## 12. Health Score Formula

```python
def calculate_health_score(metrics: DatabaseMetrics) -> HealthScore:
    score = 100

    # SQL Performance (-0 to -25)
    if metrics.sql_regressions > 0:
        score -= min(25, metrics.sql_regressions * 10)

    # Blocking (-0 to -20)
    if metrics.blocking_sessions > 0:
        score -= min(20, 20)  # Immediate -20 if any blocking

    # Storage (-0 to -15)
    max_ts_pct = max(ts.used_pct for ts in metrics.tablespaces)
    if max_ts_pct > 90:
        score -= 15
    elif max_ts_pct > 80:
        score -= 8

    # Jobs (-0 to -15)
    if metrics.failed_jobs > 0:
        score -= min(15, metrics.failed_jobs * 5)

    # Resource (-0 to -15)
    if metrics.cpu_pct > 90:
        score -= 10
    if metrics.io_rate_anomaly:
        score -= 5

    # Errors (-0 to -10)
    score -= min(10, metrics.oracle_errors * 2)

    return HealthScore(
        total=max(0, score),
        breakdown={
            "sql_performance": ...,
            "blocking": ...,
            "storage": ...,
            "jobs": ...,
            "resource": ...,
            "errors": ...
        }
    )
```

---

## 13. Audit Log Specification

Mỗi MCP tool call **bắt buộc** phải ghi audit:

```python
@dataclass
class AuditRecord:
    occurred_at: datetime
    user_id: str                     # From request context
    database_id: str
    tool_name: str
    input_args: dict                 # Sanitized (no credentials)
    duration_ms: int
    rows_returned: int | None
    status: str                      # "success" | "error" | "timeout"
    error_message: str | None
```

**Bắt buộc:**
- Audit log không được mất dù MCP tool lỗi
- Audit log phải được ghi TRƯỚC khi trả kết quả
- Input args phải được sanitize (không log credential)
- Retention: tối thiểu 1 năm

---

## 14. Oracle Permission Requirements

```sql
-- AWR / ASH
GRANT SELECT ON SYS.DBA_HIST_SQLSTAT TO db_copilot_user;
GRANT SELECT ON SYS.DBA_HIST_SQL_PLAN TO db_copilot_user;
GRANT SELECT ON SYS.DBA_HIST_SNAPSHOT TO db_copilot_user;
GRANT SELECT ON SYS.DBA_HIST_SQLTEXT TO db_copilot_user;
GRANT SELECT ON SYS.DBA_HIST_SYS_TIME_MODEL TO db_copilot_user;
GRANT SELECT ON SYS.DBA_HIST_ACTIVE_SESS_HISTORY TO db_copilot_user;

-- V$ views
GRANT SELECT ON SYS.V_$SQL TO db_copilot_user;
GRANT SELECT ON SYS.V_$SESSION TO db_copilot_user;
GRANT SELECT ON SYS.V_$SESSION_WAIT TO db_copilot_user;
GRANT SELECT ON SYS.V_$SQL_PLAN TO db_copilot_user;
GRANT SELECT ON SYS.V_$SQL_PLAN_STATISTICS_ALL TO db_copilot_user;
GRANT SELECT ON SYS.V_$SQLSTATS TO db_copilot_user;

-- Storage
GRANT SELECT ON SYS.DBA_DATA_FILES TO db_copilot_user;
GRANT SELECT ON SYS.DBA_FREE_SPACE TO db_copilot_user;
GRANT SELECT ON SYS.DBA_SEGMENTS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_TABLESPACES TO db_copilot_user;
GRANT SELECT ON SYS.DBA_TEMP_FILES TO db_copilot_user;
GRANT SELECT ON SYS.V_$TEMPSTAT TO db_copilot_user;
GRANT SELECT ON SYS.V_$UNDOSTAT TO db_copilot_user;

-- Jobs
GRANT SELECT ON SYS.DBA_SCHEDULER_JOBS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_SCHEDULER_JOB_RUN_DETAILS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_SCHEDULER_RUNNING_JOBS TO db_copilot_user;

-- Code / Objects
GRANT SELECT ON SYS.ALL_SOURCE TO db_copilot_user;
GRANT SELECT ON SYS.ALL_OBJECTS TO db_copilot_user;
GRANT SELECT ON SYS.ALL_DEPENDENCIES TO db_copilot_user;
GRANT SELECT ON SYS.ALL_ARGUMENTS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_OBJECTS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_TAB_STATISTICS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_IND_STATISTICS TO db_copilot_user;
GRANT SELECT ON SYS.DBA_INDEXES TO db_copilot_user;

-- Database info
GRANT SELECT ON SYS.V_$DATABASE TO db_copilot_user;
GRANT SELECT ON SYS.V_$INSTANCE TO db_copilot_user;
GRANT SELECT ON SYS.V_$PARAMETER TO db_copilot_user;
GRANT SELECT ON SYS.V_$SYSSTAT TO db_copilot_user;
GRANT SELECT ON SYS.V_$SYSEVENT TO db_copilot_user;
```

**Không cấp:**
- Bất kỳ DML privilege nào (INSERT, UPDATE, DELETE)
- Bất kỳ DDL privilege nào (CREATE, ALTER, DROP)
- EXECUTE trên bất kỳ procedure nào
- DBA role

---

## 15. Daily Report Specification

### 15.1 Report Template

```
# DB Morning Briefing
Cơ sở dữ liệu: {db_name}
Ngày: {date}
Thời gian tạo: {generated_at}
Health Score: {score}/100

## CRITICAL ({critical_count} items)

### [{category}] {title}
{description}
Confidence: {confidence}%
Evidence:
{evidence_list}
Recommendation: {recommendation}

## WARNING ({warning_count} items)
...

## INFO
{info_items}

## Recommendations
{numbered_list}

---
Báo cáo này được tạo tự động bởi DB Copilot.
Không có thay đổi tự động nào được thực hiện trên database.
```

### 15.2 Report Delivery

| Channel | Config | Implementation |
|---|---|---|
| Dashboard | Always | Store in `incident` table, serve via API |
| Email | `alert_channels.email` | Python `smtplib` / sendgrid |
| Slack | `alert_channels.slack_webhook` | HTTP POST to webhook URL |
| Teams | `alert_channels.teams_webhook` | HTTP POST to webhook URL |

---

---

# 🇬🇧 ENGLISH SECTION

---

## 16. System Scope

This SRS describes the detailed software specification for DB Copilot MVP, including:

- Oracle MCP Server (Evidence Gateway)
- Health Engine (Detection rules)
- Investigation Engine (AI investigation pipeline)
- Evidence Store (PostgreSQL)
- AI Diagnosis Service
- FastAPI REST API

**Not covered:**
- React Frontend (see PRD.md for UI specs)
- Detailed infrastructure provisioning
- Oracle Database administration

---

## 17. Actors & System Context

### 17.1 Human Actors

| Actor | Description |
|---|---|
| **DBA** | Primary user, receives reports and investigates incidents |
| **Database Developer** | Investigates SQL/procedure performance |
| **Backend Developer** | Understands DB issues affecting application code |
| **System Administrator** | Configures and operates the system |

### 17.2 System Actors

| System Actor | Description |
|---|---|
| **Oracle Database** | Single source of truth, read-only access |
| **LLM Provider** | OpenAI / Claude / Gemini — receives evidence, returns diagnosis |
| **PostgreSQL** | Evidence Store — persists historical data |
| **MCP Client** | AI agent or CLI calling MCP tools |

---

## 18. MCP Tool Catalog (Full)

_(Same as Section 3, in English — see tool tables above)_

All 35 tools across 7 groups:
1. SQL Tools (6)
2. Session Tools (5)
3. AWR/ASH Tools (5)
4. Storage Tools (5)
5. Job Tools (4)
6. Database Health Tools (6)
7. Code Intelligence Tools (9)

---

## 19. Evidence Model

### 19.1 Evidence Types

| Type | Oracle Source | Description |
|---|---|---|
| `sql_plan_change` | `DBA_HIST_SQLSTAT` | Execution plan changed |
| `sql_regression` | `DBA_HIST_SQLSTAT` + `V$SQL` | SQL elapsed time spiked |
| `cardinality_mismatch` | `V$SQL_PLAN_STATISTICS_ALL` | Large estimated vs actual row discrepancy |
| `high_physical_reads` | `DBA_HIST_SQLSTAT` | Disk reads increased |
| `stale_statistics` | `DBA_TAB_STATISTICS` | Object statistics too old |
| `blocking_session` | `V$SESSION` | Session being blocked |
| `tablespace_threshold` | `DBA_DATA_FILES` + `DBA_FREE_SPACE` | Tablespace exceeded threshold |
| `job_failure` | `DBA_SCHEDULER_JOB_RUN_DETAILS` | Scheduler job failed |
| `wait_event_anomaly` | `V$SESSION_WAIT` + ASH | Unusual wait event pattern |
| `long_running_session` | `V$SESSION` | Session running too long |

---

## 20. Detection Engine Rules

Rules fire before AI; deterministic logic only:

| Rule | Trigger | Severity |
|---|---|---|
| SQL Regression | `current_elapsed > avg × 3.0` | HIGH |
| CPU Spike | SQL CPU > 200% vs baseline | MEDIUM |
| Plan Change | `plan_hash_value` changed | MEDIUM |
| Cardinality Mismatch | `actual/estimated > 10` or `< 0.1` | MEDIUM |
| Tablespace Warning | `used_pct > 80` | WARNING |
| Tablespace Critical | `used_pct > 90` | CRITICAL |
| Blocking Session | Any blocking chain detected | HIGH |
| Job Failure | Any scheduler job failed | HIGH |
| Long Running Session | Session duration > threshold | MEDIUM |
| Invalid Objects | Any invalid objects found | LOW |

---

## 21. Investigation Engine Pipeline

### 21.1 Intent Parser Output

```json
{
  "type": "PROCEDURE_SLOW",
  "entities": [{"type": "PROCEDURE", "name": "PROC_SETTLEMENT"}],
  "time_range": {"begin": "2026-09-08T14:20:00Z", "end": "2026-09-08T14:45:00Z"},
  "focus_metric": "elapsed_time",
  "question_text": "Why was PROC_SETTLEMENT slow at 14:32?"
}
```

### 21.2 Investigation Plan (PROCEDURE_SLOW)

```
1. get_object_metadata (PROC_SETTLEMENT)
2. get_ash_sql_activity (time window ±15min)
3. get_sql_statistics (sql_ids from ASH)
4. get_sql_plan_history (top sql_id from step 3)
5. get_sql_wait_events (top sql_id)
6. get_awr_sql_stats (top sql_id, surrounding snapshots)
7. get_blocking_sessions
8. get_resource_usage
9. get_object_source (PROC_SETTLEMENT)
10. [correlate all evidence]
```

---

## 22. AI Diagnosis Service

### 22.1 LLM Provider Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    async def diagnose(self, evidence_package: EvidencePackage) -> DiagnosisResult:
        pass
```

### 22.2 Required LLM Output Structure

```json
{
  "diagnosis": "string",
  "confidence": 0.91,
  "primary_cause": "string",
  "evidence_used": ["string"],
  "evidence_against": ["string"],
  "recommendations": [
    {
      "action": "string",
      "sql": "string",
      "priority": "HIGH|MEDIUM|LOW",
      "note": "DBA must review and execute manually"
    }
  ],
  "confidence_explanation": "string"
}
```

---

## 23. Oracle Permission Requirements

_(See Section 14 above — full grant list applies)_

**Key principle:** SELECT-only on pre-approved views. No DML, no DDL, no EXECUTE, no DBA role.

---

## 24. Health Score Formula

Score starts at 100 and deducts:

| Category | Deduction |
|---|---|
| SQL regressions | -10 per regression (max -25) |
| Blocking sessions | -20 (any blocking = immediate deduction) |
| Tablespace > 90% | -15 |
| Tablespace 80-90% | -8 |
| Failed jobs | -5 per job (max -15) |
| CPU > 90% | -10 |
| IO anomaly | -5 |
| Oracle errors | -2 per error (max -10) |

**Final score:** `max(0, 100 - deductions)`

> Note: Score is a UX indicator only. Evidence is the actual decision basis.

---

## 25. Audit Log Specification

Every MCP tool call **must** be audit-logged:

```python
@dataclass
class AuditRecord:
    occurred_at: datetime
    user_id: str
    database_id: str
    tool_name: str
    input_args: dict       # Sanitized — no credentials
    duration_ms: int
    rows_returned: int | None
    status: str            # "success" | "error" | "timeout"
    error_message: str | None
```

**Rules:**
- Audit log must never be lost even when MCP tool errors
- Log must be written BEFORE returning results
- Minimum retention: 1 year
- Args must be sanitized (no credential logging)
