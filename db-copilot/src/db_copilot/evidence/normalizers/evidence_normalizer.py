from typing import Any

from db_copilot.db.schema import SqlBaseline
from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.models.evidence import Evidence


class EvidenceNormalizer:
    """Normalizes raw data from MCP tools or metrics into domain Evidence objects."""

    def normalize_sql_regression(
        self,
        current_elapsed_ms: float,
        baseline: SqlBaseline | None,
        sql_id: str,
        multiplier: float = 3.0,
    ) -> Evidence | None:
        """Evaluate whether a SQL execution time regressed significantly vs baseline."""
        if baseline is None or not baseline.is_reliable:
            return None

        mean_ms = float(baseline.mean_elapsed_ms) if baseline.mean_elapsed_ms is not None else 0.0
        if mean_ms <= 0:
            return None

        ratio = current_elapsed_ms / mean_ms
        if ratio < multiplier:
            return None

        severity = self._severity_from_ratio(ratio)
        return Evidence(
            type=EvidenceType.SQL_REGRESSION,
            source="sql_metrics + sql_baselines",
            entity_type="SQL",
            entity_id=sql_id,
            severity=severity,
            data={
                "sql_id": sql_id,
                "current_elapsed_ms": current_elapsed_ms,
                "baseline_mean_ms": mean_ms,
                "regression_ratio": round(ratio, 2),
                "baseline_sample_count": baseline.sample_count,
            },
            supports_hypothesis=["Execution Plan Regression", "Statistics Issue"],
        )

    def _severity_from_ratio(self, ratio: float) -> Severity:
        if ratio >= 10.0:
            return Severity.CRITICAL
        if ratio >= 5.0:
            return Severity.HIGH
        if ratio >= 3.0:
            return Severity.MEDIUM
        return Severity.LOW

    def normalize_blocking_chain(self, blocking_data: dict[str, Any]) -> list[Evidence]:
        """Convert blocking chain report into Evidence."""
        total_blocked = blocking_data.get("total_blocked", 0)
        if total_blocked <= 0:
            return []

        chains = blocking_data.get("chains", [])
        evidence_list: list[Evidence] = []

        if chains:
            for chain in chains:
                root_sid = chain.get("root_blocker_sid", "UNKNOWN")
                evidence_list.append(
                    Evidence(
                        type=EvidenceType.BLOCKING_SESSION,
                        source="get_blocking_sessions",
                        entity_type="SESSION",
                        entity_id=str(root_sid),
                        severity=Severity.HIGH,
                        data=chain,
                        supports_hypothesis=["Blocking / Concurrency Issue"],
                    )
                )
        else:
            evidence_list.append(
                Evidence(
                    type=EvidenceType.BLOCKING_SESSION,
                    source="get_blocking_sessions",
                    entity_type="SESSION",
                    entity_id="blocking_chain",
                    severity=Severity.HIGH,
                    data=blocking_data,
                    supports_hypothesis=["Blocking / Concurrency Issue"],
                )
            )

        return evidence_list

    def normalize_tablespace_usage(
        self,
        tablespaces: list[dict[str, Any]],
        warning_pct: float = 80.0,
        critical_pct: float = 90.0,
    ) -> list[Evidence]:
        """Convert tablespaces exceeding threshold into Evidence."""
        evidence_list: list[Evidence] = []
        for ts in tablespaces:
            used_pct = ts.get("used_pct", 0.0)
            if used_pct >= warning_pct:
                severity = Severity.CRITICAL if used_pct >= critical_pct else Severity.MEDIUM
                evidence_list.append(
                    Evidence(
                        type=EvidenceType.TABLESPACE_FULL,
                        source="get_tablespace_usage",
                        entity_type="TABLESPACE",
                        entity_id=ts.get("name", "UNKNOWN"),
                        severity=severity,
                        data=ts,
                        supports_hypothesis=["Storage / Tablespace Exhaustion"],
                    )
                )
        return evidence_list

    def normalize_failed_jobs(self, failed_jobs: list[dict[str, Any]]) -> list[Evidence]:
        """Convert failed scheduler jobs into Evidence."""
        evidence_list: list[Evidence] = []
        for job in failed_jobs:
            evidence_list.append(
                Evidence(
                    type=EvidenceType.JOB_FAILURE,
                    source="get_failed_jobs",
                    entity_type="JOB",
                    entity_id=job.get("job_name", "UNKNOWN"),
                    severity=Severity.HIGH,
                    data=job,
                    supports_hypothesis=["Background Job Failure"],
                )
            )
        return evidence_list

    def normalize_long_running_sessions(
        self, sessions: list[dict[str, Any]], threshold_sec: int = 1800
    ) -> list[Evidence]:
        """Convert sessions running longer than threshold into Evidence."""
        evidence_list: list[Evidence] = []
        for session in sessions:
            elapsed = session.get("elapsed_seconds") or session.get("last_call_et", 0)
            if elapsed >= threshold_sec:
                evidence_list.append(
                    Evidence(
                        type=EvidenceType.LONG_RUNNING_SESSION,
                        source="get_long_running_sessions",
                        entity_type="SESSION",
                        entity_id=str(session.get("sid", "UNKNOWN")),
                        severity=Severity.MEDIUM,
                        data=session,
                        supports_hypothesis=["Blocking / Concurrency Issue"],
                    )
                )
        return evidence_list

    def normalize_invalid_objects(self, invalid_objects: list[dict[str, Any]]) -> list[Evidence]:
        """Convert invalid schema objects into Evidence."""
        evidence_list: list[Evidence] = []
        for obj in invalid_objects:
            owner = obj.get("owner", "")
            name = obj.get("object_name", "")
            full_name = f"{owner}.{name}" if owner else name
            evidence_list.append(
                Evidence(
                    type=EvidenceType.INVALID_OBJECTS,
                    source="get_invalid_objects",
                    entity_type=obj.get("object_type", "OBJECT"),
                    entity_id=full_name,
                    severity=Severity.MEDIUM,
                    data=obj,
                )
            )
        return evidence_list
