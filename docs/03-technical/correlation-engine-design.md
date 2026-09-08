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

        # Collect thêm evidence trước khi tạo incident
        plan_history = await self.mcp.call_tool("get_sql_plan_history", {
            "sql_id": metric.sql_id, "days": 1
        })

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
                    "ratio": ratio
                }
            )
        ]

        # Kiểm tra plan change
        if len(plan_history) >= 2:
            if plan_history[-1]["plan_hash"] != plan_history[-2]["plan_hash"]:
                evidence_list.append(Evidence(
                    type=EvidenceType.SQL_PLAN_CHANGE,
                    entity_type="SQL",
                    entity_id=metric.sql_id,
                    severity=Severity.HIGH,
                    data={
                        "old_plan": plan_history[-2]["plan_hash"],
                        "new_plan": plan_history[-1]["plan_hash"],
                        "change_time": plan_history[-1]["first_seen"]
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
    Immediate severity: HIGH (bất kỳ blocking nào).
    """

    async def evaluate(self) -> Incident | None:
        blocking = await self.mcp.call_tool("get_blocking_sessions", {})

        if blocking["total_blocked"] == 0:
            return None

        return Incident(
            severity=Severity.HIGH,
            category=IncidentCategory.BLOCKING,
            title=f"Blocking detected: {blocking['total_blocked']} sessions blocked",
            description=f"Max wait: {blocking['max_wait_seconds']}s",
            evidence=[Evidence(
                type=EvidenceType.BLOCKING_SESSION,
                severity=Severity.HIGH,
                data=blocking
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

    async def evaluate(self) -> list[Incident]:
        usage_list = await self.mcp.call_tool("get_tablespace_usage", {})
        incidents = []

        for ts in usage_list:
            if ts["used_pct"] >= settings.tablespace_critical_threshold:
                sev = Severity.CRITICAL
            elif ts["used_pct"] >= settings.tablespace_warning_threshold:
                sev = Severity.MEDIUM
            else:
                continue

            # Tính growth trend từ 7 ngày lịch sử
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

    async def evaluate(self) -> list[Incident]:
        failed = await self.mcp.call_tool("get_failed_jobs", {"hours": 24})
        incidents = []

        for job in failed:
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

---

## 4. Evidence Graph

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
    Được dùng bởi Investigation Engine để tìm causal chain.
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
        ...

    def get_most_impactful_entity(self) -> GraphNode | None:
        """Entity có nhiều evidence nhất với highest severity."""
        ...
```

### 4.1 Ví dụ Evidence Graph

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
        "required_evidence": [],
        "supporting_evidence": [
            EvidenceType.HIGH_PHYSICAL_READS,
            EvidenceType.CARDINALITY_MISMATCH
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
        1. Kiểm tra required_evidence có đủ không
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
                # Có required evidence không tồn tại → skip (hoặc confidence rất thấp)
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

## 6. Correlation Engine Orchestrator

```python
# src/db_copilot/correlation/engine.py

class CorrelationEngine:
    """
    Orchestrator chính:
    1. Chạy tất cả detection rules sau mỗi collection cycle
    2. Build evidence graph
    3. Generate hypotheses
    4. Tạo/update incidents trong PostgreSQL
    """

    def __init__(self):
        self.rules = [
            SqlRegressionRule(),
            BlockingSessionRule(),
            TablespaceThresholdRule(),
            JobFailureRule(),
            LongRunningSessionRule(),
            InvalidObjectRule()
        ]
        self.hypothesis_engine = HypothesisEngine()

    async def evaluate_all(self):
        all_incidents = []

        for rule in self.rules:
            incidents = await rule.evaluate()
            if isinstance(incidents, list):
                all_incidents.extend(incidents)
            elif incidents:
                all_incidents.append(incidents)

        for incident in all_incidents:
            # Build evidence graph
            graph = EvidenceGraph()
            for evidence in incident.evidence:
                graph.add_evidence(evidence)

            # Generate hypotheses
            incident.hypotheses = self.hypothesis_engine.rank_hypotheses(
                incident.evidence
            )

            # Persist
            await self.incident_repo.upsert(incident)

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

| Rule | Trigger | Severity | Extra Evidence Collected |
|---|---|---|---|
| `SqlRegressionRule` | `elapsed > baseline × 3.0` | MEDIUM–CRITICAL | Plan history |
| `BlockingSessionRule` | Any blocking chain | HIGH | Full blocking chain |
| `TablespaceThresholdRule` | usage > 80% or > 90% | MEDIUM–CRITICAL | Growth trend |
| `JobFailureRule` | Any failed job in 24h | HIGH | Error message, last success |
| `LongRunningSessionRule` | Session > threshold | MEDIUM | Session detail |
| `InvalidObjectRule` | Any INVALID object | LOW | Object metadata |

---

## 9. Evidence Graph

Directed graph connecting entities (SQL, Procedure, Table, Session, Statistics) with typed relationships (executes, uses, accesses, blocks, depends_on).

Used by Investigation Engine to find causal chains. Edge weights reflect temporal proximity and causal likelihood.

---

## 10. Hypothesis Engine

Scores hypotheses based on:
- **Required evidence**: Must be present (0 → skip hypothesis)
- **Supporting evidence**: Each adds `confidence_boost_per_supporting`
- **Contradicting evidence**: Multiplies confidence by 0.4

Output: Sorted list of hypotheses with confidence scores (capped at 98%).

---

## 11. Hypothesis Definitions

| Hypothesis | Required | Primary Supporting |
|---|---|---|
| Statistics Issue | `stale_statistics` | `cardinality_mismatch`, `sql_regression` |
| Execution Plan Regression | `sql_plan_change` | `sql_regression`, `high_physical_reads` |
| Blocking / Concurrency | `blocking_session` | `long_running_session` |
| IO Contention | `wait_event_anomaly` | `high_physical_reads` |
| Data Volume Increase | _(none required)_ | `high_physical_reads`, `cardinality_mismatch` |
