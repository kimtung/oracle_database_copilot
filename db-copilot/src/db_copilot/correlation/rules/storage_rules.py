from __future__ import annotations

import logging
from typing import Any

from db_copilot.correlation.rules.base import BaseRule
from db_copilot.domain.enums import EvidenceType, IncidentCategory, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class TablespaceThresholdRule(BaseRule):
    """
    Deterministic rule detecting Tablespace capacity exhaustion.
    Triggers when tablespace usage exceeds warning (default 80%)
    or critical (default 90%) thresholds.
    """

    @property
    def name(self) -> str:
        return "TablespaceThresholdRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        database_id = context.get("database_id")
        tablespaces = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []

        warn_threshold = self.settings.tablespace_warning_threshold
        crit_threshold = self.settings.tablespace_critical_threshold

        for ts in tablespaces:
            if not isinstance(ts, dict):
                continue

            name = ts.get("tablespace_name")
            used_pct = float(ts.get("used_pct", 0.0))
            if not name or used_pct < warn_threshold:
                continue

            if used_pct >= crit_threshold:
                sev = Severity.CRITICAL
            elif used_pct >= 85.0:
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            # Days until full estimation if growth rate available
            days_until_full = ts.get("days_until_full")
            free_bytes = ts.get("free_bytes", 0)
            total_bytes = ts.get("total_bytes", 0)

            evidence = Evidence(
                type=EvidenceType.TABLESPACE_FULL,
                source="DBA_TABLESPACE_USAGE_METRICS",
                entity_type="TABLESPACE",
                entity_id=name,
                severity=sev,
                data={
                    "tablespace_name": name,
                    "used_pct": used_pct,
                    "free_bytes": free_bytes,
                    "total_bytes": total_bytes,
                    "days_until_full": days_until_full,
                },
                supports_hypothesis=["H4_RESOURCE_EXHAUSTION"],
            )

            title = f"Tablespace Capacity Warning: {name} ({used_pct:.1f}% used)"
            description = (
                f"Tablespace {name} has reached {used_pct:.1f}% capacity. "
                f"Free space remaining: {free_bytes / (1024 * 1024):.1f} MB."
            )
            if days_until_full is not None:
                description += f" Estimated {days_until_full:.0f} day(s) until full."

            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.TABLESPACE,
                    severity=sev,
                    title=title,
                    description=description,
                    evidence=[evidence],
                )
            )

        return incidents


class JobFailureRule(BaseRule):
    """
    Deterministic rule detecting Oracle Scheduler Job failures.
    """

    @property
    def name(self) -> str:
        return "JobFailureRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        database_id = context.get("database_id")
        jobs = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []

        for job in jobs:
            if not isinstance(job, dict):
                continue

            job_name = job.get("job_name")
            status = job.get("status")
            if not job_name or status == "SUCCEEDED":
                continue

            error_num = job.get("error_number") or job.get("error_code")
            error_msg = job.get("error_message") or job.get("additional_info") or "Unknown error"
            owner = job.get("owner", "SYS")

            evidence = Evidence(
                type=EvidenceType.JOB_FAILURE,
                source="DBA_SCHEDULER_JOB_RUN_DETAILS",
                entity_type="JOB",
                entity_id=job_name,
                severity=Severity.HIGH,
                data={
                    "job_name": job_name,
                    "owner": owner,
                    "status": status,
                    "error_number": error_num,
                    "error_message": error_msg,
                    "log_date": job.get("log_date"),
                },
                supports_hypothesis=["H5_CODE_DEFECT", "H4_RESOURCE_EXHAUSTION"],
            )

            err_tag = f"ORA-{error_num}" if error_num else "FAILED"
            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.JOB_FAILURE,
                    severity=Severity.HIGH,
                    title=f"Oracle Scheduler Job Failed: {job_name} ({err_tag})",
                    description=(
                        f"Job {owner}.{job_name} failed with error: {error_msg}."
                    ),
                    evidence=[evidence],
                )
            )

        return incidents


class InvalidObjectRule(BaseRule):
    """
    Deterministic rule detecting invalid Oracle schema objects (procedures, packages, views).
    """

    @property
    def name(self) -> str:
        return "InvalidObjectRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        database_id = context.get("database_id")
        objects = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            status = obj.get("status")
            if status != "INVALID":
                continue

            obj_name = obj.get("object_name")
            obj_type = obj.get("object_type", "OBJECT")
            owner = obj.get("owner", "UNKNOWN")
            if not obj_name:
                continue

            # Core packages / bodies have higher severity
            if obj_type in ["PACKAGE", "PACKAGE BODY", "TRIGGER"]:
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            full_name = f"{owner}.{obj_name}"
            evidence = Evidence(
                type=EvidenceType.INVALID_OBJECTS,
                source="DBA_OBJECTS",
                entity_type="OBJECT",
                entity_id=full_name,
                severity=sev,
                data={
                    "owner": owner,
                    "object_name": obj_name,
                    "object_type": obj_type,
                    "status": status,
                    "last_ddl_time": obj.get("last_ddl_time"),
                },
                supports_hypothesis=["H5_CODE_DEFECT"],
            )

            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.INVALID_OBJECT,
                    severity=sev,
                    title=f"Invalid Oracle Object: {full_name} ({obj_type})",
                    description=(
                        f"Database object {full_name} of type {obj_type} is in INVALID state."
                    ),
                    evidence=[evidence],
                )
            )

        return incidents
