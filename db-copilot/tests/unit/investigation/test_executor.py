"""Tests for InvestigationContext and InvestigationExecutor."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from db_copilot.investigation.context import InvestigationContext
from db_copilot.investigation.planner import (
    InvestigationIntent,
    InvestigationPlan,
    InvestigationStep,
)


class TestInvestigationContext:
    def test_record_step_flat_dict(self):
        ctx = InvestigationContext()
        ctx.record_step("step_1", {"sql_id": "abc123", "elapsed": 5000})
        assert ctx.dynamic_parameters["step_1.sql_id"] == "abc123"
        assert ctx.dynamic_parameters["step_1.elapsed"] == 5000

    def test_record_step_list_extracts_first_item(self):
        ctx = InvestigationContext()
        ctx.record_step("step_1", [{"sql_id": "xyz789"}, {"sql_id": "zzz"}])
        assert ctx.dynamic_parameters["step_1.sql_id"] == "xyz789"
        assert ctx.dynamic_parameters["step_1.top_sql_id"] == "xyz789"

    def test_resolve_param_static_value(self):
        ctx = InvestigationContext()
        assert ctx.resolve_param("hello") == "hello"
        assert ctx.resolve_param(42) == 42

    def test_resolve_param_dynamic_expression(self):
        ctx = InvestigationContext()
        ctx.record_step("step_1", {"sql_id": "target_id"})
        result = ctx.resolve_param("$step_1.sql_id")
        assert result == "target_id"

    def test_resolve_param_missing_key_returns_expression(self):
        ctx = InvestigationContext()
        result = ctx.resolve_param("$step_99.missing")
        assert result == "$step_99.missing"

    def test_resolve_params_dict(self):
        ctx = InvestigationContext()
        ctx.record_step("step_1", {"sql_id": "abc"})
        resolved = ctx.resolve_params({"sql_id": "$step_1.sql_id", "limit": 10})
        assert resolved == {"sql_id": "abc", "limit": 10}


class TestInvestigationExecutor:
    @pytest.mark.asyncio
    async def test_execute_single_step_success(self):
        from db_copilot.investigation.executor import InvestigationExecutor

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(return_value={"sql_id": "abc", "elapsed": 1000})

        step = InvestigationStep(
            step_id="step_1",
            tool_name="get_sql_statistics",
            params={"sql_id": "abc"},
        )
        plan = InvestigationPlan(
            intent=InvestigationIntent(),
            steps=[step],
        )

        executor = InvestigationExecutor(mcp_client=mock_mcp, step_timeout=5.0)
        ctx = await executor.execute(plan)

        assert "step_1" in ctx.step_results
        assert ctx.step_results["step_1"]["sql_id"] == "abc"
        assert ctx.errors == []

    @pytest.mark.asyncio
    async def test_optional_step_failure_continues(self):
        from db_copilot.investigation.executor import InvestigationExecutor

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(side_effect=RuntimeError("tool failed"))

        step = InvestigationStep(
            step_id="step_1",
            tool_name="get_sql_plan_history",
            params={},
            optional=True,
        )
        plan = InvestigationPlan(intent=InvestigationIntent(), steps=[step])

        executor = InvestigationExecutor(mcp_client=mock_mcp, step_timeout=5.0)
        ctx = await executor.execute(plan)

        assert "step_1" not in ctx.step_results
        assert len(ctx.warnings) == 1
        assert ctx.errors == []

    @pytest.mark.asyncio
    async def test_required_step_failure_records_error(self):
        from db_copilot.investigation.executor import InvestigationExecutor

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(side_effect=RuntimeError("required step failed"))

        step = InvestigationStep(
            step_id="step_1",
            tool_name="get_blocking_sessions",
            params={},
            optional=False,
        )
        plan = InvestigationPlan(intent=InvestigationIntent(), steps=[step])

        executor = InvestigationExecutor(mcp_client=mock_mcp, step_timeout=5.0)
        ctx = await executor.execute(plan)

        assert len(ctx.errors) == 1
        assert "required step failed" in ctx.errors[0]

    @pytest.mark.asyncio
    async def test_step_timeout_handled_gracefully(self):
        from db_copilot.investigation.executor import InvestigationExecutor

        async def slow_tool(name, params):
            await asyncio.sleep(10)

        mock_mcp = MagicMock()
        mock_mcp.call_tool = slow_tool

        step = InvestigationStep(
            step_id="step_1",
            tool_name="get_ash_sample",
            params={},
            optional=True,
        )
        plan = InvestigationPlan(intent=InvestigationIntent(), steps=[step])

        executor = InvestigationExecutor(mcp_client=mock_mcp, step_timeout=0.05)
        ctx = await executor.execute(plan)

        assert "timed out" in ctx.warnings[0].lower()

    @pytest.mark.asyncio
    async def test_dependency_skipped_when_dep_failed(self):
        from db_copilot.investigation.executor import InvestigationExecutor

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(side_effect=RuntimeError("step_1 failed"))

        steps = [
            InvestigationStep(step_id="step_1", tool_name="get_ash_sql_activity", params={}),
            InvestigationStep(
                step_id="step_2",
                tool_name="get_sql_plan",
                params={},
                dependencies=["step_1"],
            ),
        ]
        plan = InvestigationPlan(intent=InvestigationIntent(), steps=steps)

        executor = InvestigationExecutor(mcp_client=mock_mcp, step_timeout=5.0)
        ctx = await executor.execute(plan)

        # step_2 should be skipped because step_1 was never in executed set
        assert "step_2" not in ctx.step_results
