"""Investigation Intent Parser and Planner.

Converts natural-language DBA questions into structured InvestigationPlan
objects ready for execution by InvestigationExecutor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum


class IntentType(StrEnum):
    SLOW_PROCEDURE = "SLOW_PROCEDURE"
    SLOW_SQL = "SLOW_SQL"
    BLOCKING_ISSUE = "BLOCKING_ISSUE"
    SYSTEM_SLOWNESS = "SYSTEM_SLOWNESS"
    GENERAL_HEALTH = "GENERAL_HEALTH"


@dataclass
class InvestigationIntent:
    intent_type: IntentType = IntentType.GENERAL_HEALTH
    entity_type: str = "DATABASE"   # PROCEDURE | SQL | SESSION | TABLESPACE | DATABASE
    entity_id: str = ""             # procedure name, sql_id, session_id, etc.
    start_time: str = ""            # ISO 8601 or empty
    end_time: str = ""              # ISO 8601 or empty
    focus_metric: str = "general"   # execution_time | cpu | io | memory | locks | general


@dataclass
class InvestigationStep:
    """One step in an investigation plan — maps to one MCP tool call."""

    step_id: str                            # e.g. "step_1"
    tool_name: str                          # MCP tool name
    params: dict[str, object]               # static params for the tool call
    description: str = ""
    optional: bool = False                  # if True, failure of this step is non-fatal
    dependencies: list[str] = field(default_factory=list)  # step_ids that must run first


@dataclass
class InvestigationPlan:
    intent: InvestigationIntent
    steps: list[InvestigationStep]


# ── Regex patterns for intent detection (no LLM needed for common patterns) ──

_PROC_PATTERNS = [
    r"\b(slow|slow down|performance|latency|hang|timeout)\b.{0,40}\b(proc|procedure|package|pkg)\b",
    r"\b(proc|procedure|package|pkg)\b.{0,40}\b(slow|slow down|performance|latency)\b",
    r"\bwhy (was|is) (\w+) slow\b",
    r"\b(proc|procedure)\b.{0,60}(took|taking|elapsed)\b",
]
_SQL_PATTERNS = [
    r"\b(sql_id|sql id)\s*[=:]\s*([a-z0-9]+)\b",
    r"\b(query|sql|statement)\b.{0,40}\b(slow|regression|worse|degraded)\b",
    r"\bexecution plan\b",
    r"\bfull table scan\b",
]
_BLOCKING_PATTERNS = [
    r"\b(block|blocking|lock|deadlock|contention|wait)\b",
    r"\b(session|user)\b.{0,20}\bblock\w*\b",
]
_SLOWNESS_PATTERNS = [
    r"\b(system|database|db|server)\b.{0,30}\b(slow|sluggish|unresponsive|overloaded)\b",
    r"\beveryone\b.{0,20}\b(slow|affected)\b",
    r"\b(high (cpu|memory|io|load))\b",
]


class IntentParser:
    """Regex-based intent classifier for common Oracle DBA question patterns.

    Deterministic, no LLM needed. Falls back to GENERAL_HEALTH if no match.
    """

    def parse(self, question: str) -> InvestigationIntent:
        q = question.lower()
        intent = InvestigationIntent()

        # Blocking / lock first (high priority)
        if any(re.search(p, q) for p in _BLOCKING_PATTERNS):
            intent.intent_type = IntentType.BLOCKING_ISSUE
            intent.entity_type = "SESSION"
            intent.focus_metric = "locks"
            return intent

        # Procedure / package
        if any(re.search(p, q) for p in _PROC_PATTERNS):
            intent.intent_type = IntentType.SLOW_PROCEDURE
            intent.entity_type = "PROCEDURE"
            intent.focus_metric = "execution_time"
            # Try to extract procedure name
            name_match = re.search(r"\b([A-Z][A-Z0-9_]{2,})\b", question)
            if name_match:
                intent.entity_id = name_match.group(1)
            return intent

        # SQL / query
        if any(re.search(p, q) for p in _SQL_PATTERNS):
            intent.intent_type = IntentType.SLOW_SQL
            intent.entity_type = "SQL"
            intent.focus_metric = "execution_time"
            sql_match = re.search(r"\bsql.?id[=:\s]+([a-z0-9]+)\b", q)
            if sql_match:
                intent.entity_id = sql_match.group(1)
            return intent

        # System-wide slowness
        if any(re.search(p, q) for p in _SLOWNESS_PATTERNS):
            intent.intent_type = IntentType.SYSTEM_SLOWNESS
            intent.entity_type = "DATABASE"
            intent.focus_metric = "general"
            return intent

        return intent  # GENERAL_HEALTH default


class InvestigationPlanner:
    """Maps IntentType to an ordered list of MCP tool investigation steps."""

    def build_plan(self, intent: InvestigationIntent) -> InvestigationPlan:
        match intent.intent_type:
            case IntentType.SLOW_PROCEDURE:
                steps = self._plan_slow_procedure(intent)
            case IntentType.SLOW_SQL:
                steps = self._plan_slow_sql(intent)
            case IntentType.BLOCKING_ISSUE:
                steps = self._plan_blocking(intent)
            case IntentType.SYSTEM_SLOWNESS:
                steps = self._plan_system_slowness(intent)
            case _:
                steps = self._plan_general_health(intent)
        return InvestigationPlan(intent=intent, steps=steps)

    # ── Plan templates ─────────────────────────────────────────────────────────

    @staticmethod
    def _plan_slow_procedure(intent: InvestigationIntent) -> list[InvestigationStep]:
        entity = intent.entity_id or "unknown_procedure"
        return [
            InvestigationStep(
                step_id="step_1",
                tool_name="get_ash_sql_activity",
                params={"module": entity, "minutes": 60},
                description=f"Find SQL IDs executed by {entity} via ASH",
            ),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_sql_statistics",
                params={"sql_id": "$step_1.top_sql_id"},
                description="Get statistics for the top SQL ID found",
                dependencies=["step_1"],
            ),
            InvestigationStep(
                step_id="step_3",
                tool_name="get_sql_plan",
                params={"sql_id": "$step_1.top_sql_id"},
                description="Fetch current execution plan",
                dependencies=["step_1"],
            ),
            InvestigationStep(
                step_id="step_4",
                tool_name="get_sql_plan_history",
                params={"sql_id": "$step_1.top_sql_id"},
                description="Check for execution plan changes",
                optional=True,
                dependencies=["step_1"],
            ),
            InvestigationStep(
                step_id="step_5",
                tool_name="get_object_metadata",
                params={"object_name": entity, "object_type": "PROCEDURE"},
                description="Check object statistics and last DDL",
                optional=True,
            ),
        ]

    @staticmethod
    def _plan_slow_sql(intent: InvestigationIntent) -> list[InvestigationStep]:
        sql_id = intent.entity_id or ""
        params_sql: dict = {"sql_id": sql_id} if sql_id else {"limit": 10, "metric": "elapsed"}
        return [
            InvestigationStep(
                step_id="step_1",
                tool_name="get_sql_statistics" if sql_id else "get_top_sql",
                params=params_sql,
                description="Get SQL performance statistics",
            ),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_sql_plan",
                params={"sql_id": sql_id or "$step_1.sql_id"},
                description="Fetch execution plan",
                dependencies=["step_1"],
            ),
            InvestigationStep(
                step_id="step_3",
                tool_name="get_sql_plan_history",
                params={"sql_id": sql_id or "$step_1.sql_id"},
                description="Check for plan regressions",
                optional=True,
                dependencies=["step_1"],
            ),
            InvestigationStep(
                step_id="step_4",
                tool_name="get_sql_wait_events",
                params={"sql_id": sql_id or "$step_1.sql_id"},
                description="Identify dominant wait events",
                optional=True,
                dependencies=["step_1"],
            ),
        ]

    @staticmethod
    def _plan_blocking(intent: InvestigationIntent) -> list[InvestigationStep]:
        return [
            InvestigationStep(
                step_id="step_1",
                tool_name="get_blocking_sessions",
                params={},
                description="Get current blocking session chains",
            ),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_active_sessions",
                params={"status": "ACTIVE"},
                description="Get all active sessions for context",
                optional=True,
            ),
            InvestigationStep(
                step_id="step_3",
                tool_name="get_ash_sample",
                params={"minutes": 30, "event": "enq"},
                description="ASH sample for enqueue waits",
                optional=True,
            ),
        ]

    @staticmethod
    def _plan_system_slowness(intent: InvestigationIntent) -> list[InvestigationStep]:
        return [
            InvestigationStep(
                step_id="step_1",
                tool_name="get_resource_usage",
                params={},
                description="Get system resource utilisation",
            ),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_top_sql",
                params={"limit": 10, "metric": "cpu"},
                description="Top SQL by CPU",
            ),
            InvestigationStep(
                step_id="step_3",
                tool_name="get_active_sessions",
                params={},
                description="Overview of active sessions",
                optional=True,
            ),
            InvestigationStep(
                step_id="step_4",
                tool_name="get_tablespace_usage",
                params={},
                description="Check tablespace free space",
                optional=True,
            ),
        ]

    @staticmethod
    def _plan_general_health(intent: InvestigationIntent) -> list[InvestigationStep]:
        return [
            InvestigationStep(
                step_id="step_1",
                tool_name="get_database_info",
                params={},
                description="Database metadata and status",
            ),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_resource_usage",
                params={},
                description="System resource overview",
                optional=True,
            ),
            InvestigationStep(
                step_id="step_3",
                tool_name="get_top_sql",
                params={"limit": 5, "metric": "elapsed"},
                description="Top 5 SQL by elapsed time",
                optional=True,
            ),
        ]
