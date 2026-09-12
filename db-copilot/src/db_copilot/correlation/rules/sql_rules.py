from __future__ import annotations

import logging
from typing import Any

from db_copilot.correlation.rules.base import BaseRule
from db_copilot.domain.enums import EvidenceType, IncidentCategory, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class SqlRegressionRule(BaseRule):
    """
    Deterministic rule detecting SQL Performance Regressions.
    Triggers when current elapsed time exceeds baseline mean by
    >= sql_regression_multiplier (default 3.0x).
    Optionally inspects execution plan changes via Oracle MCP.
    """

    @property
    def name(self) -> str:
        return "SqlRegressionRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        baselines = context.get("baselines", {})
        database_id = context.get("database_id")

        metrics = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []

        for m in metrics:
            if not isinstance(m, dict):
                continue

            sql_id = m.get("sql_id")
            if not sql_id:
                continue

            # Check baseline
            baseline = baselines.get(sql_id)
            if not baseline:
                continue

            # Ensure baseline is reliable
            is_reliable = (
                baseline.is_reliable
                if hasattr(baseline, "is_reliable")
                else baseline.get("is_reliable", False)
            )
            if not is_reliable:
                continue

            mean_elapsed = (
                baseline.mean_elapsed_ms
                if hasattr(baseline, "mean_elapsed_ms")
                else baseline.get("mean_elapsed_ms")
            )
            if not mean_elapsed or float(mean_elapsed) <= 0:
                continue
            mean_elapsed = float(mean_elapsed)

            elapsed_time_ms = m.get("elapsed_time_ms")
            if elapsed_time_ms is None:
                # If metric has elapsed_time in microseconds or seconds
                raw_time = m.get("elapsed_time", 0)
                executions = m.get("executions", 1) or 1
                elapsed_time_ms = (raw_time / executions) / 1000.0  # convert to ms

            elapsed_time_ms = float(elapsed_time_ms)
            ratio = elapsed_time_ms / mean_elapsed
            if ratio < self.settings.sql_regression_multiplier:
                continue

            # Determine severity
            if ratio >= 10.0:
                sev = Severity.CRITICAL
            elif ratio >= 5.0:
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            # Build evidences
            evidences: list[Evidence] = []
            ev_reg = Evidence(
                type=EvidenceType.SQL_REGRESSION,
                source="V$SQLSTATS",
                entity_type="SQL",
                entity_id=sql_id,
                severity=sev,
                data={
                    "current_elapsed_ms": elapsed_time_ms,
                    "baseline_mean_ms": mean_elapsed,
                    "multiplier": round(ratio, 2),
                    "executions": m.get("executions", 1),
                },
                supports_hypothesis=["H1_PLAN_REGRESSION", "H3_STATISTICS_STALE"],
            )
            evidences.append(ev_reg)

            # Check for plan change via MCP tool get_sql_plan_history
            plan_changed = False
            try:
                plan_history = await self.mcp.call_tool(
                    "get_sql_plan_history", {"sql_id": sql_id}
                )
                if isinstance(plan_history, list) and len(plan_history) > 1:
                    plan_hashes = {
                        p.get("plan_hash_value") for p in plan_history if isinstance(p, dict)
                    }
                    if len(plan_hashes) > 1:
                        plan_changed = True
                        evidences.append(
                            Evidence(
                                type=EvidenceType.SQL_PLAN_CHANGE,
                                source="DBA_HIST_SQLSTAT",
                                entity_type="SQL",
                                entity_id=sql_id,
                                severity=sev,
                                data={
                                    "plan_count": len(plan_hashes),
                                    "plans": list(plan_hashes),
                                },
                                supports_hypothesis=["H1_PLAN_REGRESSION"],
                            )
                        )
            except Exception as exc:
                logger.debug(f"Optional plan history check for {sql_id} skipped: {exc}")

            title = f"SQL Regression detected: {sql_id} ({ratio:.1f}x baseline)"
            if plan_changed:
                title += " [Plan Changed]"

            description = (
                f"SQL statement {sql_id} average execution time is {elapsed_time_ms:.1f}ms, "
                f"which is {ratio:.1f}x higher than baseline ({mean_elapsed:.1f}ms)."
            )

            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.SQL_REGRESSION,
                    severity=sev,
                    title=title,
                    description=description,
                    evidence=evidences,
                )
            )

        return incidents
