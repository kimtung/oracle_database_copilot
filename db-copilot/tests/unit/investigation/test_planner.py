"""Tests for IntentParser and InvestigationPlanner."""

from __future__ import annotations

from db_copilot.investigation.planner import (
    IntentParser,
    IntentType,
    InvestigationIntent,
    InvestigationPlanner,
)


class TestIntentParser:
    def setup_method(self):
        self.parser = IntentParser()

    def test_parse_blocking_question(self):
        intent = self.parser.parse("Why is there a blocking lock contention in the database?")
        assert intent.intent_type == IntentType.BLOCKING_ISSUE
        assert intent.focus_metric == "locks"

    def test_parse_slow_procedure(self):
        intent = self.parser.parse("Why was PROC_SETTLEMENT slow at 14:32?")
        assert intent.intent_type == IntentType.SLOW_PROCEDURE
        assert intent.entity_type == "PROCEDURE"

    def test_parse_slow_sql_with_sql_id(self):
        intent = self.parser.parse("sql_id=abc123def query is degraded")
        assert intent.intent_type == IntentType.SLOW_SQL
        assert intent.entity_id == "abc123def"

    def test_parse_system_slowness(self):
        intent = self.parser.parse("The database is very slow and everyone is affected")
        assert intent.intent_type == IntentType.SYSTEM_SLOWNESS

    def test_parse_general_health_default(self):
        intent = self.parser.parse("Show me a database overview")
        assert intent.intent_type == IntentType.GENERAL_HEALTH

    def test_blocking_takes_priority_over_procedure(self):
        intent = self.parser.parse("PROC_SETTLEMENT is blocking other sessions")
        assert intent.intent_type == IntentType.BLOCKING_ISSUE


class TestInvestigationPlanner:
    def setup_method(self):
        self.planner = InvestigationPlanner()

    def test_slow_procedure_plan_has_ash_step(self):
        intent = InvestigationIntent(intent_type=IntentType.SLOW_PROCEDURE, entity_id="PROC_X")
        plan = self.planner.build_plan(intent)
        tool_names = [s.tool_name for s in plan.steps]
        assert "get_ash_sql_activity" in tool_names
        assert "get_sql_plan" in tool_names

    def test_blocking_plan_has_blocking_sessions_step(self):
        intent = InvestigationIntent(intent_type=IntentType.BLOCKING_ISSUE)
        plan = self.planner.build_plan(intent)
        assert plan.steps[0].tool_name == "get_blocking_sessions"

    def test_slow_sql_plan_has_statistics_and_plan(self):
        intent = InvestigationIntent(intent_type=IntentType.SLOW_SQL, entity_id="abc123")
        plan = self.planner.build_plan(intent)
        tool_names = [s.tool_name for s in plan.steps]
        assert "get_sql_statistics" in tool_names
        assert "get_sql_plan" in tool_names

    def test_step_dependencies_defined(self):
        intent = InvestigationIntent(intent_type=IntentType.SLOW_PROCEDURE, entity_id="P")
        plan = self.planner.build_plan(intent)
        dep_steps = [s for s in plan.steps if s.dependencies]
        # Subsequent steps should depend on step_1
        assert all("step_1" in s.dependencies for s in dep_steps)

    def test_system_slowness_plan_has_resource_usage(self):
        intent = InvestigationIntent(intent_type=IntentType.SYSTEM_SLOWNESS)
        plan = self.planner.build_plan(intent)
        assert plan.steps[0].tool_name == "get_resource_usage"
