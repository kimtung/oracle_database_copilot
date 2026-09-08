# Test Plan
# Kế Hoạch Kiểm Thử

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Chiến Lược Kiểm Thử Tổng Quan

Hệ thống gồm hai project: `oracle-mcp-server` và `db-copilot`. Mỗi project có test strategy riêng.

### Test Pyramid

```
                 /\
                /  \
               / E2E \        ← Scenarios (ít nhất)
              /────────\
             / Integrat. \    ← Với Oracle & PostgreSQL
            /────────────\
           /  Unit Tests   \  ← Nhiều nhất, nhanh nhất
          /────────────────\
```

---

## 2. oracle-mcp-server Test Strategy

### 2.1 Unit Tests

**Location:** `oracle-mcp-server/tests/unit/`

**Approach:** Mock Oracle connection, test tool logic và output schema.

```python
# tests/unit/tools/test_sql_tools.py

import pytest
from unittest.mock import AsyncMock, patch
from oracle_mcp.tools.sql import get_sql_statistics
from oracle_mcp.models.sql_models import SqlStatistics

@pytest.mark.asyncio
async def test_get_sql_statistics_returns_correct_schema():
    """
    Test tool trả về đúng schema, không phụ thuộc Oracle thật.
    """
    mock_row = {
        "sql_id": "8f3abc",
        "sql_text": "SELECT * FROM ACCOUNT_POSITION ...",
        "executions": 12450,
        "elapsed_time": 52300000,
        "cpu_time": 21300000,
        "buffer_gets": 182000000,
        "disk_reads": 9300000,
        "rows_processed": 4200000,
        "last_active_time": "2026-09-08 14:32:00",
        "plan_hash_value": 98237412,
        "module": "PROC_SETTLEMENT",
        "action": "UPDATE_PHASE"
    }

    with patch("oracle_mcp.oracle.repositories.sql_repo.SqlRepository.get_sql_statistics",
               new_callable=AsyncMock) as mock_repo:
        mock_repo.return_value = SqlStatistics(**mock_row)

        result = await get_sql_statistics(sql_id="8f3abc")

        assert result["sql_id"] == "8f3abc"
        assert result["executions"] == 12450
        assert result["module"] == "PROC_SETTLEMENT"

@pytest.mark.asyncio
async def test_get_blocking_sessions_returns_empty_when_no_blocking():
    with patch(...) as mock_repo:
        mock_repo.return_value = {"blocking_chains": [], "total_blocked": 0}
        result = await get_blocking_sessions()
        assert result["total_blocked"] == 0

@pytest.mark.asyncio
async def test_audit_log_written_on_success():
    """Audit log phải được ghi dù kết quả thế nào."""
    with patch("oracle_mcp.security.audit._write_audit_log") as mock_audit:
        await get_sql_statistics(sql_id="abc123")
        mock_audit.assert_called_once()
        call_args = mock_audit.call_args[0]
        assert call_args[3] == "success"  # status

@pytest.mark.asyncio
async def test_audit_log_written_on_error():
    with patch("oracle_mcp.oracle.repositories.sql_repo.SqlRepository.get_sql_statistics",
               side_effect=Exception("ORA-00942: table or view does not exist")):
        with patch("oracle_mcp.security.audit._write_audit_log") as mock_audit:
            with pytest.raises(Exception):
                await get_sql_statistics(sql_id="bad")
            mock_audit.assert_called_once()
            assert mock_audit.call_args[0][3] == "error"
```

**Danh sách test cases bắt buộc:**

| Test | Group | Priority |
|---|---|---|
| `get_sql_statistics` trả về đúng schema | SQL | P0 |
| `get_blocking_sessions` trả về empty khi không có blocking | Session | P0 |
| `get_blocking_sessions` trả về full chain khi có blocking | Session | P0 |
| `get_tablespace_usage` trả về usage% đúng | Storage | P0 |
| `get_object_source` trả về source + sql_statements | Object | P0 |
| Audit log ghi khi success | Security | P0 |
| Audit log ghi khi error | Security | P0 |
| Credentials không xuất hiện trong audit log | Security | P0 |
| Tool trả về structured error khi Oracle unreachable | Reliability | P0 |

### 2.2 Integration Tests

**Location:** `oracle-mcp-server/tests/integration/`

**Requirement:** Cần Oracle test instance (Docker Oracle XE hoặc Oracle Free)

```python
# tests/integration/test_oracle_connection.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_oracle_connection_pool_initializes():
    """Test kết nối thật đến Oracle."""
    pool = await OracleConnectionPool.initialize()
    assert pool is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_top_sql_returns_real_data():
    """Test với Oracle thật, kiểm tra data format."""
    result = await get_top_sql(metric="elapsed_time", limit=5, hours=1)
    assert isinstance(result, list)
    for sql in result:
        assert "sql_id" in sql
        assert len(sql["sql_id"]) == 13  # Oracle SQL_ID là 13 ký tự
```

---

## 3. db-copilot Test Strategy

### 3.1 Unit Tests

**Location:** `db-copilot/tests/unit/`

#### 3.1.1 Detection Rules Tests

```python
# tests/unit/correlation/test_sql_rules.py

@pytest.mark.asyncio
async def test_sql_regression_detected_when_ratio_exceeds_threshold():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=10_000)
    baseline = SqlBaseline(mean_elapsed_ms=2_000, is_reliable=True, sample_count=10)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is not None
    assert incident.category == IncidentCategory.SQL_REGRESSION
    assert incident.severity == Severity.HIGH  # ratio = 5x

@pytest.mark.asyncio
async def test_sql_regression_not_detected_when_baseline_unreliable():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=10_000)
    baseline = SqlBaseline(mean_elapsed_ms=2_000, is_reliable=False, sample_count=3)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is None  # Không detect khi baseline unreliable

@pytest.mark.asyncio
async def test_sql_regression_not_detected_when_ratio_below_threshold():
    current = SqlMetric(sql_id="abc", elapsed_time_ms=5_000)
    baseline = SqlBaseline(mean_elapsed_ms=3_000, is_reliable=True, sample_count=10)

    rule = SqlRegressionRule(multiplier=3.0, mcp_client=AsyncMock())
    incident = await rule.evaluate(current, baseline)

    assert incident is None  # ratio = 1.67x < 3.0

@pytest.mark.asyncio
async def test_tablespace_critical_when_above_90_pct():
    ts_data = [{"name": "APP_DATA", "used_pct": 92.5}]
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = ts_data

    rule = TablespaceThresholdRule(mcp_client=mock_mcp, warning=80, critical=90)
    incidents = await rule.evaluate()

    assert len(incidents) == 1
    assert incidents[0].severity == Severity.CRITICAL
```

#### 3.1.2 Hypothesis Engine Tests

```python
# tests/unit/correlation/test_hypothesis_engine.py

def test_blocking_hypothesis_has_highest_confidence_when_blocking_detected():
    evidence = [
        Evidence(type=EvidenceType.BLOCKING_SESSION, severity=Severity.HIGH, data={}),
        Evidence(type=EvidenceType.LONG_RUNNING_SESSION, severity=Severity.MEDIUM, data={}),
    ]
    engine = HypothesisEngine()
    hypotheses = engine.rank_hypotheses(evidence)

    assert hypotheses[0].name == "Blocking / Concurrency Issue"
    assert hypotheses[0].confidence > 0.90

def test_statistics_issue_hypothesis_confidence_increases_with_supporting_evidence():
    # Only stale statistics
    evidence_weak = [Evidence(type=EvidenceType.STALE_STATISTICS, data={})]
    # Stale statistics + cardinality mismatch + regression
    evidence_strong = [
        Evidence(type=EvidenceType.STALE_STATISTICS, data={}),
        Evidence(type=EvidenceType.CARDINALITY_MISMATCH, data={}),
        Evidence(type=EvidenceType.SQL_REGRESSION, data={}),
    ]

    engine = HypothesisEngine()
    h_weak = engine.rank_hypotheses(evidence_weak)
    h_strong = engine.rank_hypotheses(evidence_strong)

    stats_weak = next(h for h in h_weak if h.name == "Statistics Issue")
    stats_strong = next(h for h in h_strong if h.name == "Statistics Issue")

    assert stats_strong.confidence > stats_weak.confidence

def test_blocking_hypothesis_confidence_reduced_when_no_blocking():
    evidence = [
        Evidence(type=EvidenceType.SQL_REGRESSION, data={}),
        Evidence(type=EvidenceType.SQL_PLAN_CHANGE, data={}),
        # NO blocking_session evidence
    ]
    engine = HypothesisEngine()
    hypotheses = engine.rank_hypotheses(evidence)

    blocking_h = next((h for h in hypotheses if h.name == "Blocking / Concurrency Issue"), None)
    # Không có required evidence → không có trong kết quả
    assert blocking_h is None
```

#### 3.1.3 Investigation Engine Tests

```python
# tests/unit/investigation/test_executor.py

@pytest.mark.asyncio
async def test_investigation_completes_within_60_seconds():
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"data": "mocked"}

    executor = InvestigationExecutor(mcp_client=mock_mcp, ai_service=AsyncMock())

    start = time.time()
    result = await executor.execute("Why was PROC_SETTLEMENT slow at 14:32?")
    duration = time.time() - start

    assert duration < 60.0
    assert result is not None

@pytest.mark.asyncio
async def test_investigation_continues_when_optional_step_fails():
    """Investigation không fail khi optional step timeout."""
    mock_mcp = AsyncMock()
    async def mock_call(tool, args):
        if tool == "get_object_source":
            raise asyncio.TimeoutError()
        return {"data": "ok"}

    mock_mcp.call_tool = mock_call
    executor = InvestigationExecutor(mcp_client=mock_mcp, ai_service=AsyncMock())

    result = await executor.execute("Why was PROC_SETTLEMENT slow?")
    # Không raise exception
    assert result is not None
    # Source code error được ghi lại
    assert "get_object_source" in result.context_errors
```

### 3.2 Integration Tests

**Location:** `db-copilot/tests/integration/`

```python
# tests/integration/test_evidence_collection.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sql_collector_saves_to_postgresql():
    """Test với PostgreSQL thật (Docker compose)."""
    collector = SqlCollector(real_mcp_client, real_evidence_repo)
    await collector.collect()

    metrics = await real_evidence_repo.get_recent_sql_metrics(hours=1)
    assert len(metrics) > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_baseline_calculation_with_7_days_data():
    """Test baseline với data thật trong PostgreSQL."""
    await seed_7_days_sql_data(real_evidence_repo)
    engine = BaselineEngine(real_evidence_repo)
    await engine.recalculate()

    baseline = await real_evidence_repo.get_baseline("test_sql_id", hour=14, dow=0)
    assert baseline is not None
    assert baseline.is_reliable
    assert baseline.sample_count >= 5

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sql_regression_incident_created_when_detected():
    await seed_baseline(sql_id="abc", mean_ms=1000)
    await seed_current_metric(sql_id="abc", elapsed_ms=8000)  # 8x regression

    engine = CorrelationEngine(real_repos)
    await engine.evaluate_all()

    incidents = await real_incident_repo.get_open_incidents()
    sql_incidents = [i for i in incidents if i.category == IncidentCategory.SQL_REGRESSION]
    assert len(sql_incidents) >= 1
```

---

## 4. End-to-End Scenarios

**Location:** `db-copilot/tests/scenarios/`

Ba scenarios này là **success criteria** của toàn bộ MVP:

### Scenario 1 — Auto Detection

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_1_auto_detection():
    """
    SQL regression trong DB → Collector phát hiện → Rule engine tạo incident
    → Evidence có đủ thông tin → Daily report gửi đến DBA
    """
    # 1. Seed baseline với normal performance
    await seed_7_days_baseline(sql_id="test_sql", mean_ms=500)

    # 2. Inject slow SQL metric (giả lập regression)
    await inject_slow_sql_metric(sql_id="test_sql", elapsed_ms=5000)  # 10x

    # 3. Trigger collection cycle
    await SqlCollector(mcp_client, repo).collect()

    # 4. Trigger detection
    await CorrelationEngine(repos).evaluate_all()

    # 5. Check incident created
    incidents = await incident_repo.get_open_incidents()
    assert any(i.category == IncidentCategory.SQL_REGRESSION for i in incidents)

    # 6. Generate daily report
    report = await report_service.generate_daily_report()
    assert "SQL Regression" in report.content_markdown
    assert "test_sql" in report.content_markdown
```

### Scenario 2 — SQL Investigation

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_2_sql_investigation():
    """
    User: "Why was SQL_ID 8f3abc slow yesterday?"
    → Investigation Engine → Evidence-based Diagnosis
    """
    result = await investigation_service.investigate(
        "Why was SQL_ID 8f3abc slow yesterday?"
    )

    assert result is not None
    assert result.diagnosis.confidence > 0.5
    assert len(result.evidence) > 0
    assert result.diagnosis.confidence_explanation != ""

    # Đảm bảo recommendations không có "Execute"
    for rec in result.diagnosis.recommendations:
        assert "DBA must review" in rec.note or "manually" in rec.note
```

### Scenario 3 — Procedure Investigation ⭐

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_scenario_3_procedure_investigation():
    """
    User: "Why was PROC_SETTLEMENT slow at 14:32?"
    → Procedure → SQL → Plan → ASH → Wait → Source → Diagnosis
    """
    import time
    start = time.time()

    result = await investigation_service.investigate(
        "Why was PROC_SETTLEMENT slow at 14:32?"
    )

    duration = time.time() - start

    # Performance requirement
    assert duration < 60.0, f"Investigation took {duration:.1f}s, exceeds 60s limit"

    # Result quality
    assert result.intent.type == IntentType.PROCEDURE_SLOW
    assert len(result.evidence) >= 3, "Must have at least 3 evidence items"
    assert result.diagnosis.confidence > 0.0
    assert len(result.diagnosis.recommendations) > 0

    # Recommendations must not suggest auto-execution
    for rec in result.diagnosis.recommendations:
        assert "automatically" not in rec.action.lower()
        assert "auto" not in rec.action.lower()
```

---

## 5. Security Tests

```python
# tests/unit/security/test_credential_handling.py

def test_oracle_credentials_not_in_audit_log():
    """Credentials tuyệt đối không được xuất hiện trong audit log."""
    from oracle_mcp.security.sanitizer import sanitize_args

    args_with_creds = {
        "sql_id": "abc123",
        "user": "db_copilot_readonly",
        "password": "SECRET_PASSWORD",
        "dsn": "prod-host:1521/ORCL"
    }

    sanitized = sanitize_args(args_with_creds)

    assert "SECRET_PASSWORD" not in str(sanitized)
    assert "password" not in sanitized  # key cũng bị remove
    assert sanitized["sql_id"] == "abc123"  # non-sensitive fields giữ nguyên

def test_llm_provider_does_not_receive_oracle_credentials():
    """Evidence package gửi cho LLM không chứa credentials."""
    package = EvidencePackage(
        question="Why slow?",
        intent=mock_intent,
        evidence=[],
        hypotheses=[]
    )

    # Serialized package không được có credential-like fields
    serialized = json.dumps(dataclasses.asdict(package))
    assert "password" not in serialized
    assert "oracle_user" not in serialized
    assert "oracle_dsn" not in serialized

def test_ai_recommendations_never_include_execute_keyword():
    """Mọi AI recommendation phải là for human review."""
    # Mock LLM trả về recommendation có "execute"
    diagnosis = DiagnosisResult(
        recommendations=[
            Recommendation(
                action="Execute: EXEC DBMS_STATS.GATHER...",
                sql="EXEC DBMS_STATS.GATHER...",
                priority="HIGH",
                note="Run this automatically"  # Bad!
            )
        ]
    )

    # Validation layer phải flag/fix này
    validated = validate_recommendations(diagnosis.recommendations)
    for rec in validated:
        assert "automatically" not in rec.note.lower()
```

---

## 6. Performance Tests

```python
# tests/performance/test_investigation_performance.py

@pytest.mark.performance
@pytest.mark.asyncio
async def test_investigation_completes_in_60_seconds():
    """Investigation time phải < 60 giây."""
    times = []
    for _ in range(5):
        start = time.time()
        await executor.execute("Why was PROC_SETTLEMENT slow?")
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]

    assert avg_time < 45.0, f"Average investigation time {avg_time:.1f}s exceeds 45s"
    assert p95_time < 60.0, f"P95 investigation time {p95_time:.1f}s exceeds 60s"

@pytest.mark.performance
@pytest.mark.asyncio
async def test_mcp_tool_responds_in_5_seconds():
    """Mỗi MCP tool call phải < 5 giây."""
    tools = ["get_top_sql", "get_blocking_sessions", "get_tablespace_usage"]

    for tool in tools:
        start = time.time()
        await mcp_client.call_tool(tool, {})
        duration = time.time() - start
        assert duration < 5.0, f"Tool {tool} took {duration:.1f}s"
```

---

## 7. Test Data Management

### 7.1 Oracle Test Account Setup

```sql
-- Script tạo test data trong Oracle test instance

-- Tạo slow SQL (giả lập regression)
DECLARE
  v_count NUMBER;
BEGIN
  FOR i IN 1..1000000 LOOP
    SELECT COUNT(*) INTO v_count FROM ALL_OBJECTS WHERE OBJECT_TYPE = 'TABLE';
  END LOOP;
END;
/

-- Tạo blocking session
-- Session 1 (chạy trong background):
UPDATE TEST_TABLE SET STATUS = 'LOCKED' WHERE ID = 1;

-- Session 2 (sẽ bị block):
UPDATE TEST_TABLE SET STATUS = 'UPDATE' WHERE ID = 1;
```

### 7.2 PostgreSQL Test Data Seeding

```python
# tests/fixtures/seed_data.py

async def seed_7_days_baseline(sql_id: str, mean_ms: float):
    """Seed 7 ngày dữ liệu để có reliable baseline."""
    base_time = datetime.utcnow() - timedelta(days=7)
    for day in range(7):
        for hour in range(24):
            captured_at = base_time + timedelta(days=day, hours=hour)
            # Add some variance (±10%)
            elapsed = mean_ms * random.uniform(0.9, 1.1)
            await repo.insert_sql_metric(SqlMetric(
                sql_id=sql_id,
                captured_at=captured_at,
                elapsed_time_ms=int(elapsed)
            ))
```

---

---

# 🇬🇧 ENGLISH SECTION

---

## 8. Test Strategy Overview

Two projects, each with unit → integration → E2E test layers.

| Level | oracle-mcp-server | db-copilot |
|---|---|---|
| **Unit** | Mock Oracle, test tool output schema | Mock MCP, test rules/engine |
| **Integration** | Real Oracle (Docker XE) | Real PostgreSQL (Docker) |
| **E2E / Scenarios** | — | 3 MVP scenarios with mocked Oracle |

---

## 9. Key Unit Test Requirements

### oracle-mcp-server
- Every tool returns correct Pydantic schema
- Audit log written on both success and error
- Credentials never appear in audit log
- Server returns structured error (not crash) on Oracle unreachable

### db-copilot
- SQL regression NOT detected when baseline unreliable
- SQL regression detected when `current > baseline × multiplier`
- Hypothesis confidence increases with supporting evidence
- Investigation continues when optional step fails (no crash)
- AI recommendations never suggest automatic execution

---

## 10. E2E Scenario Acceptance Criteria

| Scenario | Must Pass For MVP |
|---|---|
| **Scenario 1** — Auto Detection | SQL regression auto-detected and included in daily report |
| **Scenario 2** — SQL Investigation | Investigation returns evidence-backed diagnosis with confidence > 0.5 |
| **Scenario 3** — Procedure Investigation | Investigation completes in < 60s, produces ≥ 3 evidence items |

---

## 11. Security Test Requirements

- Oracle credentials must never appear in audit logs
- Evidence package sent to LLM must not contain Oracle credentials
- All AI recommendations must include "DBA must review manually" note
- No `execute_sql()` style tool in oracle-mcp-server

---

## 12. Performance Requirements

| Metric | Target |
|---|---|
| Investigation total time | < 60 seconds (p95) |
| MCP tool response | < 5 seconds per tool |
| Dashboard load time | < 3 seconds |
| Evidence collection cycle | < 3 minutes (5-minute interval, must complete before next cycle) |
