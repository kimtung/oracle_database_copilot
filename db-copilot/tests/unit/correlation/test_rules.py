from unittest.mock import AsyncMock

import pytest

from db_copilot.config.settings import Settings
from db_copilot.correlation.rules import (
    BlockingSessionRule,
    InvalidObjectRule,
    JobFailureRule,
    LongRunningSessionRule,
    SqlRegressionRule,
    TablespaceThresholdRule,
)
from db_copilot.domain.enums import EvidenceType, IncidentCategory, Severity


@pytest.fixture
def mock_mcp():
    mcp = AsyncMock()
    mcp.call_tool = AsyncMock(return_value=[])
    return mcp


@pytest.fixture
def test_settings():
    return Settings(
        sql_regression_multiplier=3.0,
        tablespace_warning_threshold=80.0,
        tablespace_critical_threshold=90.0,
        long_running_threshold_sec=1800,
    )


@pytest.mark.asyncio
async def test_sql_regression_rule_triggers_and_detects_plan_change(mock_mcp, test_settings):
    # Mock plan change with 2 distinct plan hashes
    mock_mcp.call_tool.return_value = [
        {"plan_hash_value": 111111},
        {"plan_hash_value": 222222},
    ]
    rule = SqlRegressionRule(mcp_client=mock_mcp, settings=test_settings)

    metrics = [
        {"sql_id": "sql_regress_1", "elapsed_time_ms": 600.0, "executions": 10},
        {"sql_id": "sql_normal", "elapsed_time_ms": 110.0, "executions": 10},
    ]
    baselines = {
        "sql_regress_1": {"mean_elapsed_ms": 100.0, "is_reliable": True},
        "sql_normal": {"mean_elapsed_ms": 100.0, "is_reliable": True},
    }

    incidents = await rule.evaluate(metrics, context={"baselines": baselines})
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.category == IncidentCategory.SQL_REGRESSION
    assert inc.severity == Severity.HIGH  # 6.0x -> HIGH (>= 5.0x)
    assert "[Plan Changed]" in inc.title

    evidence_types = [e.type for e in inc.evidence]
    assert EvidenceType.SQL_REGRESSION in evidence_types
    assert EvidenceType.SQL_PLAN_CHANGE in evidence_types


@pytest.mark.asyncio
async def test_sql_regression_rule_ignores_unreliable_baseline(mock_mcp, test_settings):
    rule = SqlRegressionRule(mcp_client=mock_mcp, settings=test_settings)
    metrics = [{"sql_id": "sql_unreliable", "elapsed_time_ms": 5000.0}]
    baselines = {
        "sql_unreliable": {"mean_elapsed_ms": 100.0, "is_reliable": False},
    }
    incidents = await rule.evaluate(metrics, context={"baselines": baselines})
    assert len(incidents) == 0


@pytest.mark.asyncio
async def test_blocking_session_rule_triggers_on_contention(test_settings):
    rule = BlockingSessionRule(settings=test_settings)
    chain_data = [
        {
            "root_blocker": {
                "sid": 101,
                "serial": 1234,
                "program": "app.exe",
                "wait_event": "enq: TX - row lock contention",
            },
            "blocked_sessions": [{"sid": 201}, {"sid": 202}],
            "max_wait_seconds": 120,
        },
        {
            "root_blocker": {"sid": 301},
            "blocked_sessions": [],
        },
    ]

    incidents = await rule.evaluate(chain_data)
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.category == IncidentCategory.BLOCKING
    assert inc.severity == Severity.HIGH
    assert inc.evidence[0].data["blocker_sid"] == 101
    assert inc.evidence[0].data["blocked_count"] == 2


@pytest.mark.asyncio
async def test_long_running_session_rule(test_settings):
    rule = LongRunningSessionRule(settings=test_settings)
    sessions = [
        {"sid": 401, "elapsed_seconds": 3700, "username": "BATCH_USER", "sql_id": "sql_batch"},
        {"sid": 402, "elapsed_seconds": 500, "username": "WEB_USER"},
    ]

    incidents = await rule.evaluate(sessions)
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.category == IncidentCategory.LONG_RUNNING_SESSION
    assert inc.severity == Severity.HIGH  # >= 3600s
    assert inc.evidence[0].data["sid"] == 401


@pytest.mark.asyncio
async def test_tablespace_threshold_rule(test_settings):
    rule = TablespaceThresholdRule(settings=test_settings)
    tablespaces = [
        {"tablespace_name": "TS_CRITICAL", "used_pct": 95.5, "free_bytes": 1024 * 1024 * 10},
        {"tablespace_name": "TS_WARNING", "used_pct": 82.0, "free_bytes": 1024 * 1024 * 100},
        {"tablespace_name": "TS_OK", "used_pct": 50.0},
    ]

    incidents = await rule.evaluate(tablespaces)
    assert len(incidents) == 2
    assert incidents[0].severity == Severity.CRITICAL
    assert incidents[0].evidence[0].entity_id == "TS_CRITICAL"
    assert incidents[1].severity == Severity.MEDIUM
    assert incidents[1].evidence[0].entity_id == "TS_WARNING"


@pytest.mark.asyncio
async def test_job_failure_rule(test_settings):
    rule = JobFailureRule(settings=test_settings)
    jobs = [
        {
            "job_name": "GATHER_STATS_JOB",
            "status": "FAILED",
            "error_number": "12012",
            "error_message": "ORA-12012: error on auto execute of job",
            "owner": "SYS",
        },
        {"job_name": "SUCCESS_JOB", "status": "SUCCEEDED"},
    ]

    incidents = await rule.evaluate(jobs)
    assert len(incidents) == 1
    assert incidents[0].category == IncidentCategory.JOB_FAILURE
    assert incidents[0].severity == Severity.HIGH
    assert "GATHER_STATS_JOB" in incidents[0].title


@pytest.mark.asyncio
async def test_invalid_object_rule(test_settings):
    rule = InvalidObjectRule(settings=test_settings)
    objects = [
        {
            "owner": "APP_OWNER",
            "object_name": "PKG_PAYMENT",
            "object_type": "PACKAGE BODY",
            "status": "INVALID",
        },
        {"owner": "APP_OWNER", "object_name": "TBL_USER", "status": "VALID"},
    ]

    incidents = await rule.evaluate(objects)
    assert len(incidents) == 1
    assert incidents[0].category == IncidentCategory.INVALID_OBJECT
    assert incidents[0].severity == Severity.HIGH  # PACKAGE BODY -> HIGH
    assert "APP_OWNER.PKG_PAYMENT" in incidents[0].title
