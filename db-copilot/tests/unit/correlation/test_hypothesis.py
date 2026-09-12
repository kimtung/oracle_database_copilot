from db_copilot.correlation.graph import EvidenceGraph
from db_copilot.correlation.hypothesis_engine import HypothesisEngine
from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.models.evidence import Evidence


def test_hypothesis_ranking_lock_contention():
    engine = HypothesisEngine()

    ev_block = Evidence(
        type=EvidenceType.BLOCKING_SESSION,
        entity_type="SESSION",
        entity_id="101",
        severity=Severity.HIGH,
        data={
            "blocker_sid": 101,
            "blocked_sessions": [{"sid": 201}],
            "wait_event": "enq: TX - row lock contention",
        },
        supports_hypothesis=["H2_LOCK_CONTENTION"],
    )

    graph = EvidenceGraph.build_from_evidences([ev_block])
    ranked = engine.rank_hypotheses([ev_block], graph=graph)

    assert len(ranked) > 0
    top = ranked[0]
    assert "H2: Row/Table Lock Contention" in top.name
    # Direct evidence (+0.50) + explicit tag (+0.50) or graph (+0.20) -> clamped at 1.0 or >= 0.70
    assert top.confidence >= 0.70
    assert len(top.supporting_evidence) > 0


def test_hypothesis_ranking_sql_plan_regression():
    engine = HypothesisEngine()

    ev_reg = Evidence(
        type=EvidenceType.SQL_REGRESSION,
        entity_type="SQL",
        entity_id="sql_bad_plan",
        severity=Severity.HIGH,
        data={"multiplier": 4.5},
        supports_hypothesis=["H1_PLAN_REGRESSION"],
    )
    ev_plan = Evidence(
        type=EvidenceType.SQL_PLAN_CHANGE,
        entity_type="SQL",
        entity_id="sql_bad_plan",
        severity=Severity.HIGH,
        data={"plans": [111, 222]},
        supports_hypothesis=["H1_PLAN_REGRESSION"],
    )

    graph = EvidenceGraph.build_from_evidences([ev_reg, ev_plan])
    ranked = engine.rank_hypotheses([ev_reg, ev_plan], graph=graph)

    assert len(ranked) > 0
    top = ranked[0]
    assert "H1: SQL Execution Plan Regression" in top.name
    assert top.confidence >= 0.80


def test_hypothesis_ranking_resource_exhaustion():
    engine = HypothesisEngine()

    ev_ts = Evidence(
        type=EvidenceType.TABLESPACE_FULL,
        entity_type="TABLESPACE",
        entity_id="USERS",
        severity=Severity.CRITICAL,
        data={"used_pct": 98.5},
        supports_hypothesis=["H4_RESOURCE_EXHAUSTION"],
    )

    ranked = engine.rank_hypotheses([ev_ts])
    assert len(ranked) == 1
    top = ranked[0]
    assert "H4: Resource Capacity Exhaustion" in top.name
    assert top.confidence >= 0.50
