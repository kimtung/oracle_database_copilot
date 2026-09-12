from datetime import UTC, datetime

from db_copilot.db.schema import SqlBaseline
from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.evidence.normalizers.evidence_normalizer import EvidenceNormalizer


def test_normalize_sql_regression_detected():
    normalizer = EvidenceNormalizer()
    baseline = SqlBaseline(
        sql_id="sql_123",
        hour_of_day=10,
        day_of_week=1,
        sample_count=10,
        mean_elapsed_ms=100.0,
        is_reliable=True,
        calculated_at=datetime.now(UTC),
    )

    # 6x ratio -> HIGH
    ev_high = normalizer.normalize_sql_regression(600.0, baseline, sql_id="sql_123")
    assert ev_high is not None
    assert ev_high.type == EvidenceType.SQL_REGRESSION
    assert ev_high.severity == Severity.HIGH
    assert ev_high.data["regression_ratio"] == 6.0

    # 12x ratio -> CRITICAL
    ev_crit = normalizer.normalize_sql_regression(1200.0, baseline, sql_id="sql_123")
    assert ev_crit is not None
    assert ev_crit.severity == Severity.CRITICAL


def test_normalize_sql_regression_unreliable_or_below_threshold():
    normalizer = EvidenceNormalizer()
    unreliable_baseline = SqlBaseline(
        sql_id="sql_123",
        hour_of_day=10,
        day_of_week=1,
        sample_count=2,
        mean_elapsed_ms=100.0,
        is_reliable=False,
    )
    # Unreliable baseline returns None
    assert normalizer.normalize_sql_regression(800.0, unreliable_baseline, "sql_123") is None

    # None baseline returns None
    assert normalizer.normalize_sql_regression(800.0, None, "sql_123") is None

    # Below multiplier returns None (200ms / 100ms = 2.0x < 3.0x)
    reliable_baseline = SqlBaseline(
        sql_id="sql_123",
        hour_of_day=10,
        day_of_week=1,
        sample_count=10,
        mean_elapsed_ms=100.0,
        is_reliable=True,
    )
    res = normalizer.normalize_sql_regression(200.0, reliable_baseline, "sql_123", multiplier=3.0)
    assert res is None


def test_normalize_blocking_chain():
    normalizer = EvidenceNormalizer()

    # No blocked sessions
    assert normalizer.normalize_blocking_chain({"total_blocked": 0}) == []

    # Blocked chain
    blocking_payload = {
        "total_blocked": 2,
        "chains": [
            {
                "root_blocker_sid": 105,
                "blocked_sessions": [204, 305],
                "wait_event": "enq: TX - row lock contention",
            }
        ],
    }
    evidence = normalizer.normalize_blocking_chain(blocking_payload)
    assert len(evidence) == 1
    assert evidence[0].type == EvidenceType.BLOCKING_SESSION
    assert evidence[0].entity_id == "105"
    assert evidence[0].severity == Severity.HIGH


def test_normalize_tablespace_usage():
    normalizer = EvidenceNormalizer()
    tablespaces = [
        {"name": "SYSTEM", "used_pct": 72.0},
        {"name": "USERS", "used_pct": 84.5},
        {"name": "APP_DATA", "used_pct": 92.1},
    ]
    evidence = normalizer.normalize_tablespace_usage(
        tablespaces, warning_pct=80.0, critical_pct=90.0
    )
    assert len(evidence) == 2

    users_ev = next(e for e in evidence if e.entity_id == "USERS")
    app_ev = next(e for e in evidence if e.entity_id == "APP_DATA")

    assert users_ev.severity == Severity.MEDIUM
    assert app_ev.severity == Severity.CRITICAL


def test_normalize_failed_jobs():
    normalizer = EvidenceNormalizer()
    failed_jobs = [
        {"job_name": "SYNC_CUSTOMERS", "error_code": "ORA-12012", "error_message": "Job error"},
        {"job_name": "PURGE_LOGS", "error_code": "ORA-04031", "error_message": "Shared memory"},
    ]
    evidence = normalizer.normalize_failed_jobs(failed_jobs)
    assert len(evidence) == 2
    assert evidence[0].type == EvidenceType.JOB_FAILURE
    assert evidence[0].entity_id == "SYNC_CUSTOMERS"


def test_normalize_long_running_sessions_and_invalid_objects():
    normalizer = EvidenceNormalizer()
    sessions = [
        {"sid": 45, "elapsed_seconds": 300},
        {"sid": 89, "elapsed_seconds": 2400},
    ]
    ev_sessions = normalizer.normalize_long_running_sessions(sessions, threshold_sec=1800)
    assert len(ev_sessions) == 1
    assert ev_sessions[0].entity_id == "89"
    assert ev_sessions[0].type == EvidenceType.LONG_RUNNING_SESSION

    invalid_objs = [
        {"owner": "APP", "object_name": "TRG_AUDIT", "object_type": "TRIGGER", "status": "INVALID"}
    ]
    ev_objs = normalizer.normalize_invalid_objects(invalid_objs)
    assert len(ev_objs) == 1
    assert ev_objs[0].entity_id == "APP.TRG_AUDIT"
    assert ev_objs[0].type == EvidenceType.INVALID_OBJECTS
