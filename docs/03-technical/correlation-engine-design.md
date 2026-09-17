# Correlation Engine Design
# Thiết Kế Correlation Engine

**Project:** `db-copilot` — `correlation/`  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan

Correlation Engine là layer phân tích evidence để:

1. **Phát hiện anomaly** (Detection Rules) — deterministic, không dùng AI
2. **Liên kết evidence** (Evidence Graph) — build graph quan hệ giữa entities
3. **Tạo Incident** — khi phát hiện vấn đề thực sự
4. **Cung cấp hypothesis** (Hypothesis Engine) — xếp hạng các nguyên nhân có thể

### Nguyên tắc quan trọng

> **Detection Rules chạy trước AI.** AI chỉ được gọi sau khi đã có đủ evidence từ deterministic rules.

---

## 2. Component Overview

```
db-copilot/correlation/
│
├── rules/
│   ├── sql_rules.py      # SQL regression, plan change, cardinality
│   ├── session_rules.py  # Blocking sessions, long running
│   └── storage_rules.py  # Tablespace threshold, temp, undo
│
├── graph.py              # Evidence graph builder
└── engine.py             # Orchestrator: chạy rules → incidents → hypotheses
```

---

## 3. Detection Rules (Deterministic)

### 3.1 SQL Regression Rule

```python
# src/db_copilot/correlation/rules/sql_rules.py

class SqlRegressionRule:
    """
    Phát hiện SQL có elapsed time tăng so với historical baseline.

    Thresholds:
    - multiplier >= 3.0  → Trigger (configurable)
    - sample_count >= 5  → Baseline reliable

    Baseline: 7-day rolling window, same hour_of_day + day_of_week bucket.
    """

    async def evaluate(
        self,
        metric: SqlMetric,
        baseline: SqlBaseline | None
    ) -> Incident | None:

        if baseline is None or not baseline.is_reliable:
            return None

        ratio = metric.elapsed_time_ms / baseline.mean_elapsed_ms

        if ratio < settings.sql_regression_multiplier:
            return None

        # Kiểm tra plan change từ PostgreSQL metrics history (KHÔNG gọi MCP trực tiếp trong rule)
        plan_changed = False
        previous_metric = await self.repo.get_previous_sql_metric(metric.sql_id)
        if previous_metric and previous_metric.plan_hash_value != metric.plan_hash_value:
            plan_changed = True

        evidence_list = [
            Evidence(
                type=EvidenceType.SQL_REGRESSION,
                entity_type="SQL",
                entity_id=metric.sql_id,
                severity=self._severity(ratio),
                data={
                    "sql_id": metric.sql_id,
                    "current_elapsed_ms": metric.elapsed_time_ms,
                    "baseline_avg_ms": baseline.mean_elapsed_ms,
                    "ratio": ratio,
                    "plan_hash_value": metric.plan_hash_value,
                }
            )
        ]

        if plan_changed and previous_metric:
            evidence_list.append(Evidence(
                type=EvidenceType.SQL_PLAN_CHANGE,
                entity_type="SQL",
                entity_id=metric.sql_id,
                severity=Severity.HIGH,
                data={
                    "old_plan": previous_metric.plan_hash_value,
                    "new_plan": metric.plan_hash_value,
                    "previous_timestamp": str(previous_metric.timestamp),
                }
            ))

        return Incident(
            severity=Severity.HIGH if ratio >= 5 else Severity.MEDIUM,
            category=IncidentCategory.SQL_REGRESSION,
            title=f"SQL Regression: {metric.sql_id} ({ratio:.1f}x slower)",
            description=f"SQL {metric.sql_id} elapsed time increased {ratio:.1f}x vs baseline",
            evidence=evidence_list
        )

    def _severity(self, ratio: float) -> Severity:
        if ratio >= 10: return Severity.CRITICAL
        if ratio >= 5:  return Severity.HIGH
        return Severity.MEDIUM
```

### 3.2 Blocking Session Rule

```python
class BlockingSessionRule:
    """
    Phát hiện blocking session chains.
    Severity phân tầng theo thời gian chờ và số session bị block (tránh Alert Fatigue):
    - Wait < 30s VÀ <= 2 sessions  → MEDIUM
    - Wait 30s-300s HOẶC 3-9 sessions → HIGH
    - Wait > 300s HOẶC >= 10 sessions → CRITICAL
    """

    async def evaluate(self, blocking_data: dict) -> Incident | None:
        total_blocked = blocking_data.get("total_blocked", 0)
        max_wait = blocking_data.get("max_wait_seconds", 0)

        if total_blocked == 0:
            return None

        # Severity scaling
        if max_wait > 300 or total_blocked >= 10:
            sev = Severity.CRITICAL
        elif max_wait >= 30 or total_blocked >= 3:
            sev = Severity.HIGH
        else:
            sev = Severity.MEDIUM

        return Incident(
            severity=sev,
            category=IncidentCategory.BLOCKING,
            title=f"Blocking detected: {total_blocked} sessions blocked",
            description=f"Max wait: {max_wait}s (Severity: {sev.value})",
            evidence=[Evidence(
                type=EvidenceType.BLOCKING_SESSION,
                severity=sev,
                data=blocking_data
            )]
        )
```

### 3.3 Tablespace Threshold Rule

```python
class TablespaceThresholdRule:
    """
    WARNING: > 80% used
    CRITICAL: > 90% used
    Include: growth trend (bytes/day), estimated_days_until_full
    """

    async def evaluate(self, usage_list: list[dict]) -> list[Incident]:
        incidents = []

        for ts in usage_list:
            if ts["used_pct"] >= settings.tablespace_critical_threshold:
                sev = Severity.CRITICAL
            elif ts["used_pct"] >= settings.tablespace_warning_threshold:
                sev = Severity.MEDIUM
            else:
                continue

            # Tính growth trend từ 7 ngày lịch sử trong PostgreSQL
            trend = await self._calculate_growth_trend(ts["name"])

            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.TABLESPACE,
                title=f"Tablespace {ts['name']}: {ts['used_pct']:.1f}% used",
                evidence=[Evidence(
                    type=EvidenceType.TABLESPACE_THRESHOLD,
                    severity=sev,
                    data={
                        "tablespace_name": ts["name"],
                        "used_pct": ts["used_pct"],
                        "used_bytes": ts["used_bytes"],
                        "free_bytes": ts["free_bytes"],
                        "growth_bytes_per_day": trend.bytes_per_day,
                        "estimated_days_until_full": trend.days_until_full
                    }
                )]
            ))

        return incidents
```

### 3.4 Job Failure Rule

```python
class JobFailureRule:
    """
    Phát hiện scheduler jobs thất bại trong 24h qua.
    """

    async def evaluate(self, failed_jobs: list[dict]) -> list[Incident]:
        incidents = []

        for job in failed_jobs:
            incidents.append(Incident(
                severity=Severity.HIGH,
                category=IncidentCategory.JOB_FAILURE,
                title=f"Job Failed: {job['job_name']}",
                evidence=[Evidence(
                    type=EvidenceType.JOB_FAILURE,
                    severity=Severity.HIGH,
                    data={
                        "job_name": job["job_name"],
                        "error_message": job["error_message"],
                        "run_duration": job["run_duration"],
                        "last_successful_run": job["last_successful_run"]
                    }
                )]
            ))

        return incidents
```

### 3.5 Long Running Session Rule

```python
class LongRunningSessionRule:
    """
    Phát hiện session chạy lâu vượt quá ngưỡng cho phép (mặc định > 1800s / 30 phút).
    Severity:
    - >= 7200s (2h) → CRITICAL
    - >= 3600s (1h) → HIGH
    - >= 1800s (30m) → MEDIUM
    """

    async def evaluate(self, sessions: list[dict]) -> list[Incident]:
        incidents = []
        threshold_sec = settings.long_running_threshold_sec

        for s in sessions:
            elapsed_sec = s.get("elapsed_seconds", 0)
            if elapsed_sec < threshold_sec:
                continue

            if elapsed_sec >= 7200:
                sev = Severity.CRITICAL
            elif elapsed_sec >= 3600:
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            minutes = elapsed_sec // 60
            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.LONG_RUNNING_SESSION,
                title=f"Long Running Session: SID {s.get('sid')} ({minutes}m)",
                description=f"Session SID {s.get('sid')} active for {minutes}m running SQL {s.get('sql_id')}",
                evidence=[Evidence(
                    type=EvidenceType.LONG_RUNNING_SESSION,
                    severity=sev,
                    data=s
                )]
            ))

        return incidents
```

### 3.6 Invalid Object Rule

```python
class InvalidObjectRule:
    """
    Phát hiện schema objects chuyển sang trạng thái INVALID.
    Severity:
    - PACKAGE BODY, PROCEDURE, FUNCTION, TRIGGER quan trọng → MEDIUM / HIGH
    - Các đối tượng khác → LOW
    """

    async def evaluate(self, invalid_objects: list[dict]) -> list[Incident]:
        incidents = []

        for obj in invalid_objects:
            obj_type = obj.get("object_type", "UNKNOWN")
            sev = Severity.HIGH if obj_type in ("PACKAGE BODY", "PROCEDURE", "TRIGGER") else Severity.LOW

            incidents.append(Incident(
                severity=sev,
                category=IncidentCategory.INVALID_OBJECT,
                title=f"Invalid Object: {obj.get('object_name')} ({obj_type})",
                description=f"Object {obj.get('object_name')} owned by {obj.get('owner')} is INVALID",
                evidence=[Evidence(
                    type=EvidenceType.INVALID_OBJECT,
                    severity=sev,
                    data=obj
                )]
            ))

        return incidents
```

---

## 4. Evidence Graph & Relationship Modeling

> [!NOTE]
> **Phạm vi áp dụng (Scope Clarity):**
> Trong chu kỳ đánh giá Anomaly định kỳ (MVP Correlation Cycle), hệ thống sử dụng **flat evidence list** để tạo Incident và xếp hạng Hypothesis nhằm đảm bảo hiệu năng và tính đơn giản.
> `EvidenceGraph` cùng thuật toán duyệt đồ thị BFS (`get_causal_chain`, `get_most_impactful_entity`) được sử dụng trong **Investigation Engine (Phase 3)** khi người dùng yêu cầu điều tra chuyên sâu đa tầng (Multi-hop Causal Tracing: Procedure → SQL → Plan → Table → Statistics).

```python
# src/db_copilot/correlation/graph.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GraphNode:
    entity_type: str    # "SQL", "PROCEDURE", "TABLE", "SESSION"
    entity_id: str
    evidence: list[Evidence] = field(default_factory=list)

@dataclass
class GraphEdge:
    source: GraphNode
    target: GraphNode
    relationship: str   # "executes", "uses", "accesses", "blocks", "depends_on"
    weight: float       # 0.0 – 1.0 (temporal proximity + causal likelihood)

class EvidenceGraph:
    """
    Build directed evidence graph từ evidence collection.
    Chuyên biệt phục vụ Investigation Engine để tìm causal chain đa tầng.
    """

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_evidence(self, evidence: Evidence) -> GraphNode:
        key = f"{evidence.entity_type}:{evidence.entity_id}"
        if key not in self.nodes:
            self.nodes[key] = GraphNode(evidence.entity_type, evidence.entity_id)
        self.nodes[key].evidence.append(evidence)
        return self.nodes[key]

    def add_relationship(
        self,
        source_type: str, source_id: str,
        relationship: str,
        target_type: str, target_id: str,
        weight: float = 0.5
    ):
        source_key = f"{source_type}:{source_id}"
        target_key = f"{target_type}:{target_id}"

        source = self.nodes.get(source_key)
        target = self.nodes.get(target_key)

        if source and target:
            self.edges.append(GraphEdge(source, target, relationship, weight))

    def get_causal_chain(self, root_entity: str) -> list[GraphEdge]:
        """BFS từ root entity, trả về ordered causal chain."""
        visited = set()
        queue = [root_entity]
        chain = []

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            for edge in self.edges:
                curr_key = f"{edge.source.entity_type}:{edge.source.entity_id}"
                if curr_key == curr:
                    target_key = f"{edge.target.entity_type}:{edge.target.entity_id}"
                    if target_key not in visited:
                        chain.append(edge)
                        queue.append(target_key)
        return chain

    def get_most_impactful_entity(self) -> GraphNode | None:
        """Entity có nhiều evidence nhất với highest severity."""
        if not self.nodes:
            return None
        return max(
            self.nodes.values(),
            key=lambda n: (
                max((e.severity.value for e in n.evidence), default="LOW"),
                len(n.evidence)
            )
        )
```

### 4.1 Ví dụ Evidence Graph trong Investigation Engine

```
PROC_SETTLEMENT (PROCEDURE)
      │
      │ executes [via ASH MODULE]
      ▼
SQL_ID 8f3abc (SQL)
      │
      │ plan_changed [DBA_HIST_SQLSTAT]
      ▼
PLAN 98237412 (PLAN)
      │
      │ accesses [from plan operations]
      ▼
ACCOUNT_POSITION (TABLE)
      │
      │ stale_statistics [DBA_TAB_STATISTICS]
      ▼
LAST_ANALYZED: 18 days ago (STATISTICS)
```

---

## 5. Hypothesis Engine

```python
# src/db_copilot/correlation/engine.py

HYPOTHESIS_DEFINITIONS = [
    {
        "name": "Statistics Issue",
        "required_evidence": [EvidenceType.STALE_STATISTICS],
        "supporting_evidence": [
            EvidenceType.CARDINALITY_MISMATCH,
            EvidenceType.SQL_REGRESSION,
            EvidenceType.HIGH_PHYSICAL_READS
        ],
        "base_confidence": 0.70,
        "confidence_boost_per_supporting": 0.08,
        "contradicted_by": [EvidenceType.BLOCKING_SESSION]
    },
    {
        "name": "Execution Plan Regression",
        "required_evidence": [EvidenceType.SQL_PLAN_CHANGE],
        "supporting_evidence": [
            EvidenceType.SQL_REGRESSION,
            EvidenceType.HIGH_PHYSICAL_READS,
            EvidenceType.CARDINALITY_MISMATCH
        ],
        "base_confidence": 0.65,
        "confidence_boost_per_supporting": 0.08,
        "contradicted_by": []
    },
    {
        "name": "Blocking / Concurrency Issue",
        "required_evidence": [EvidenceType.BLOCKING_SESSION],
        "supporting_evidence": [EvidenceType.LONG_RUNNING_SESSION],
        "base_confidence": 0.90,
        "confidence_boost_per_supporting": 0.05,
        "contradicted_by": []
    },
    {
        "name": "IO Contention",
        "required_evidence": [EvidenceType.WAIT_EVENT_ANOMALY],  # db file sequential read
        "supporting_evidence": [EvidenceType.HIGH_PHYSICAL_READS],
        "base_confidence": 0.55,
        "confidence_boost_per_supporting": 0.10,
        "contradicted_by": []
    },
    {
        "name": "Data Volume Increase",
        # [CE-04]: Phải có CARDINALITY_MISMATCH thì mới kích hoạt hypothesis này, tránh noise
        "required_evidence": [EvidenceType.CARDINALITY_MISMATCH],
        "supporting_evidence": [
            EvidenceType.HIGH_PHYSICAL_READS,
        ],
        "base_confidence": 0.40,
        "confidence_boost_per_supporting": 0.12,
        "contradicted_by": [EvidenceType.SQL_PLAN_CHANGE, EvidenceType.STALE_STATISTICS]
    }
]

class HypothesisEngine:
    def rank_hypotheses(self, evidence_list: list[Evidence]) -> list[Hypothesis]:
        """
        Với mỗi hypothesis definition:
        1. Kiểm tra required_evidence có đủ không (nếu thiếu -> skip hoàn toàn)
        2. Đếm supporting_evidence
        3. Kiểm tra contradicting_evidence
        4. Tính confidence score
        5. Sort by confidence DESC
        """
        results = []
        evidence_types = {e.type for e in evidence_list}

        for defn in HYPOTHESIS_DEFINITIONS:
            # Check required
            required = set(defn["required_evidence"])
            if required and not required.issubset(evidence_types):
                # Có required evidence không tồn tại → skip
                continue

            # Count supporting
            supporting_count = sum(
                1 for et in defn["supporting_evidence"]
                if et in evidence_types
            )

            # Check contradicting
            is_contradicted = any(
                et in evidence_types
                for et in defn.get("contradicted_by", [])
            )

            # Calculate confidence
            confidence = defn["base_confidence"]
            confidence += supporting_count * defn["confidence_boost_per_supporting"]
            if is_contradicted:
                confidence *= 0.4  # Giảm mạnh confidence

            confidence = min(0.98, confidence)  # Cap at 98%

            results.append(Hypothesis(
                name=defn["name"],
                confidence=confidence,
                supporting_evidence=[
                    e for e in evidence_list if e.type in defn["supporting_evidence"]
                ],
                contradicting_evidence=[
                    e for e in evidence_list if e.type in defn.get("contradicted_by", [])
                ]
            ))

        return sorted(results, key=lambda h: h.confidence, reverse=True)
```

---

## 6. Correlation Engine Orchestrator & Incident Deduplication

### 6.1 Chiến lược Deduplication (Chống bão Alert)
- **Vấn đề [CE-05]:** Khi SQL bị chậm kéo dài 30 phút, nếu mỗi cycle 5 phút sinh 1 incident mới thì DBA sẽ nhận 6 incidents duplicate rác.
- **Giải pháp:**
  - Kiểm tra xem trong database đã có Incident nào cùng `(database_id, category, entity_id)` đang ở trạng thái `OPEN` hoặc `INVESTIGATING` trong vòng **60 phút** vừa qua không.
  - Nếu đã tồn tại: Cập nhật incident cũ (`last_seen_at = now()`, cập nhật severity nếu cao hơn, append evidence mới vào incident hiện có).
  - Nếu chưa có: Tạo mới incident.
  - Tầng PostgreSQL hỗ trợ index: `CREATE INDEX idx_incidents_dedup ON incidents (database_id, category, status, detected_at);`

```python
# src/db_copilot/correlation/engine.py

class CorrelationEngine:
    """
    Orchestrator chính:
    1. Chạy tất cả detection rules sau mỗi collection cycle
    2. Gom flat evidence list
    3. Generate hypotheses
    4. Deduplicate và Lưu/Cập nhật incidents trong PostgreSQL
    """

    def __init__(self, incident_repo: IncidentRepository):
        self.incident_repo = incident_repo
        self.rules = [
            SqlRegressionRule(),
            BlockingSessionRule(),
            TablespaceThresholdRule(),
            JobFailureRule(),
            LongRunningSessionRule(),
            InvalidObjectRule()
        ]
        self.hypothesis_engine = HypothesisEngine()

    async def evaluate_all(self, collected_data: dict, context: dict):
        all_incidents = []

        # 1. Chạy tất cả detection rules trên dữ liệu đã thu thập
        for rule in self.rules:
            incidents = await rule.evaluate(collected_data.get(rule.name), context)
            if isinstance(incidents, list):
                all_incidents.extend(incidents)
            elif incidents:
                all_incidents.append(incidents)

        # 2. Deduplicate và lưu trữ Incident
        for incident in all_incidents:
            # Generate hypotheses trên flat evidence list
            incident.hypotheses = self.hypothesis_engine.rank_hypotheses(
                incident.evidence
            )

            # Deduplication: kiểm tra incident tương tự đang OPEN trong 60 phút
            existing = await self.incident_repo.find_open_incident(
                database_id=incident.database_id,
                category=incident.category,
                entity_id=incident.evidence[0].entity_id if incident.evidence else None,
                within_minutes=60
            )

            if existing:
                # Merge evidence và nâng severity nếu cần
                await self.incident_repo.append_evidence(existing.id, incident.evidence)
                if incident.severity > existing.severity:
                    await self.incident_repo.update_severity(existing.id, incident.severity)
            else:
                await self.incident_repo.create_incident(incident)

    async def evaluate_for_investigation(
        self,
        evidence_list: list[Evidence]
    ) -> list[Hypothesis]:
        """
        Được gọi bởi Investigation Engine để generate hypotheses
        cho một investigation cụ thể.
        """
        return self.hypothesis_engine.rank_hypotheses(evidence_list)
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 7. Overview

Correlation Engine is the layer that analyzes evidence to:

1. **Detect anomalies** (Detection Rules) — deterministic, no AI
2. **Link evidence** (Evidence Graph) — build relationship graph between entities
3. **Create Incidents** — when real issues are detected
4. **Generate Hypotheses** — rank possible root causes

### Core Principle

> **Detection Rules run before AI.** AI is only called after deterministic rules have collected sufficient evidence.

---

## 8. Detection Rules Summary

| Rule | Trigger | Severity | Extra Evidence Collected | Architecture Note |
|---|---|---|---|---|
| `SqlRegressionRule` | `elapsed > baseline × 3.0` | MEDIUM–CRITICAL | `plan_hash_value` change | Compare with historical metrics in DB; **no MCP call inside rule** |
| `BlockingSessionRule` | Total blocked > 0 | MEDIUM–CRITICAL | Full blocking tree | Scaled by wait time & blocked count to prevent alert fatigue |
| `TablespaceThresholdRule` | usage > 80% or > 90% | MEDIUM–CRITICAL | Growth trend | From 7-day snapshot metrics |
| `JobFailureRule` | Any failed job in 24h | HIGH | Error message, last success | Filtered by run history |
| `LongRunningSessionRule` | Active session > 1800s | MEDIUM–CRITICAL | Session context | Scaled: 30m (MEDIUM), 1h (HIGH), 2h (CRITICAL) |
| `InvalidObjectRule` | Any INVALID object | LOW–HIGH | Object metadata | HIGH for packages/procedures/triggers |

---

## 9. Evidence Graph & Investigation Engine

> [!NOTE]
> **Scope & MVP Execution:**
> In the scheduled correlation cycle (MVP), a **flat evidence list** is processed to create Incidents and rank Hypotheses with high speed and deterministic guarantees.
> The `EvidenceGraph` and its BFS causal chain algorithms (`get_causal_chain`, `get_most_impactful_entity`) are dedicated to the **Investigation Engine (Phase 3)** for deep interactive multi-hop root-cause tracing.

---

## 10. Hypothesis Engine

Scores hypotheses based on:
- **Required evidence**: Must be present in the evidence list (if missing → skip hypothesis entirely)
- **Supporting evidence**: Each adds `confidence_boost_per_supporting`
- **Contradicting evidence**: Multiplies confidence by 0.4
- **Deduplication & Noise Filter**: All hypotheses require relevant evidence to trigger (e.g. Data Volume Increase requires `cardinality_mismatch`).

Output: Sorted list of hypotheses with confidence scores (capped at 98%).

---

## 11. Hypothesis Definitions

| Hypothesis | Required Evidence | Primary Supporting Evidence | Contradicted By |
|---|---|---|---|
| Statistics Issue | `stale_statistics` | `cardinality_mismatch`, `sql_regression` | `blocking_session` |
| Execution Plan Regression | `sql_plan_change` | `sql_regression`, `high_physical_reads` | _(none)_ |
| Blocking / Concurrency | `blocking_session` | `long_running_session` | _(none)_ |
| IO Contention | `wait_event_anomaly` | `high_physical_reads` | _(none)_ |
| Data Volume Increase | `cardinality_mismatch` | `high_physical_reads` | `sql_plan_change`, `stale_statistics` |

---

## 12. Incident Deduplication Strategy

To prevent alert fatigue and notification storms when an issue persists over multiple 5-minute cycles:
1. When a rule triggers an incident for an entity, query the repository for an existing `OPEN` or `INVESTIGATING` incident matching `(database_id, category, entity_id)` within a **60-minute deduplication window**.
2. If an open incident exists:
   - Update `last_seen_at = now()`.
   - Upgrade `severity` if the new occurrence is more severe.
   - Append new evidence to the existing incident's evidence collection.
3. If no open incident exists: Create a new incident.
4. Database level: Deduplication index on `(database_id, category, status, detected_at)`.

