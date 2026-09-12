from __future__ import annotations

import logging
from typing import Any

from db_copilot.correlation.rules.base import BaseRule
from db_copilot.domain.enums import EvidenceType, IncidentCategory, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class BlockingSessionRule(BaseRule):
    """
    Deterministic rule detecting Oracle lock contention and blocking session trees.
    Triggers when active blockers are holding locks preventing other sessions from progressing.
    """

    @property
    def name(self) -> str:
        return "BlockingSessionRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        database_id = context.get("database_id")
        chains = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []

        for chain in chains:
            if not isinstance(chain, dict):
                continue

            root_blocker = chain.get("root_blocker") or {}
            blocked_sessions = chain.get("blocked_sessions") or []

            # Also support flat structure where chain itself is the blocker
            blocker_sid = (
                root_blocker.get("sid")
                or chain.get("blocker_sid")
                or chain.get("blocking_sid")
            )
            if not blocker_sid:
                continue

            blocked_count = len(blocked_sessions) or chain.get("total_blocked", 0)
            if blocked_count <= 0:
                continue

            wait_event = (
                root_blocker.get("wait_event")
                or chain.get("wait_event")
                or "enq: TX - row lock contention"
            )
            max_wait_sec = chain.get("max_wait_seconds", 0)

            # Severity determination
            if blocked_count >= 5 or max_wait_sec >= 300:
                sev = Severity.CRITICAL
            else:
                sev = Severity.HIGH

            evidence = Evidence(
                type=EvidenceType.BLOCKING_SESSION,
                source="V$SESSION",
                entity_type="SESSION",
                entity_id=str(blocker_sid),
                severity=sev,
                data={
                    "blocker_sid": blocker_sid,
                    "blocker_serial": root_blocker.get("serial") or chain.get("blocker_serial"),
                    "blocker_program": root_blocker.get("program") or chain.get("program"),
                    "blocker_sql_id": root_blocker.get("sql_id") or chain.get("sql_id"),
                    "blocked_count": blocked_count,
                    "blocked_sessions": blocked_sessions,
                    "wait_event": wait_event,
                    "max_wait_seconds": max_wait_sec,
                },
                supports_hypothesis=["H2_LOCK_CONTENTION"],
            )

            title = (
                f"Lock Contention: Blocker SID {blocker_sid} blocking "
                f"{blocked_count} session(s)"
            )
            description = (
                f"Session SID {blocker_sid} is holding lock ({wait_event}) "
                f"and blocking {blocked_count} other user session(s)."
            )

            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.BLOCKING,
                    severity=sev,
                    title=title,
                    description=description,
                    evidence=[evidence],
                )
            )

        return incidents


class LongRunningSessionRule(BaseRule):
    """
    Deterministic rule detecting sessions running longer than configured threshold.
    """

    @property
    def name(self) -> str:
        return "LongRunningSessionRule"

    async def evaluate(self, data: Any, context: dict[str, Any] | None = None) -> list[Incident]:
        context = context or {}
        database_id = context.get("database_id")
        sessions = data if isinstance(data, list) else [data]
        incidents: list[Incident] = []
        threshold_sec = self.settings.long_running_threshold_sec

        for s in sessions:
            if not isinstance(s, dict):
                continue

            sid = s.get("sid")
            elapsed_sec = s.get("elapsed_seconds") or s.get("elapsed_time_sec", 0)
            if not sid or elapsed_sec < threshold_sec:
                continue

            # Determine severity
            if elapsed_sec >= 7200:  # >= 2 hours
                sev = Severity.CRITICAL
            elif elapsed_sec >= 3600:  # >= 1 hour
                sev = Severity.HIGH
            else:
                sev = Severity.MEDIUM

            minutes = elapsed_sec // 60
            evidence = Evidence(
                type=EvidenceType.LONG_RUNNING_SESSION,
                source="V$SESSION",
                entity_type="SESSION",
                entity_id=str(sid),
                severity=sev,
                data={
                    "sid": sid,
                    "serial": s.get("serial"),
                    "username": s.get("username"),
                    "sql_id": s.get("sql_id"),
                    "elapsed_seconds": elapsed_sec,
                    "program": s.get("program"),
                },
                supports_hypothesis=["H2_LOCK_CONTENTION", "H1_PLAN_REGRESSION"],
            )

            incidents.append(
                Incident(
                    database_id=database_id,
                    category=IncidentCategory.LONG_RUNNING_SESSION,
                    severity=sev,
                    title=f"Long running session detected: SID {sid} ({minutes}m)",
                    description=(
                        f"Session SID {sid} (user: {s.get('username') or 'UNKNOWN'}) "
                        f"has been active for {minutes} minutes running SQL ID: {s.get('sql_id')}."
                    ),
                    evidence=[evidence],
                )
            )

        return incidents
