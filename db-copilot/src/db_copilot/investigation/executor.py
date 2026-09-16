"""InvestigationExecutor — executes investigation steps via MCP client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from db_copilot.investigation.context import InvestigationContext
from db_copilot.investigation.planner import InvestigationPlan, InvestigationStep
from db_copilot.mcp.client import OracleMcpClient

logger = logging.getLogger(__name__)


class InvestigationExecutor:
    """Executes investigation steps sequentially, respecting dependencies.

    Per-step timeout (default 10 s) prevents any single MCP call from
    blocking the whole investigation.  Optional steps that fail are recorded
    as warnings and execution continues.
    """

    def __init__(
        self,
        mcp_client: OracleMcpClient,
        step_timeout: float = 10.0,
    ) -> None:
        self._client = mcp_client
        self._timeout = step_timeout

    async def execute(self, plan: InvestigationPlan) -> InvestigationContext:
        """Execute all steps in the plan and return the populated context."""
        ctx = InvestigationContext()
        executed: set[str] = set()

        for step in plan.steps:
            if not self._deps_satisfied(step, executed):
                msg = (
                    f"Skipping {step.step_id}: unmet dependencies {step.dependencies}"
                )
                logger.warning(msg)
                ctx.warnings.append(msg)
                continue

            result = await self._run_step(step, ctx)
            if result is not None:
                ctx.record_step(step.step_id, result)
                executed.add(step.step_id)

        return ctx

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _run_step(
        self,
        step: InvestigationStep,
        ctx: InvestigationContext,
    ) -> Any | None:
        resolved_params = ctx.resolve_params(step.params)
        logger.debug(
            "Executing %s: tool=%s params=%s", step.step_id, step.tool_name, resolved_params
        )
        try:
            result = await asyncio.wait_for(
                self._client.call_tool(step.tool_name, resolved_params),
                timeout=self._timeout,
            )
            return result
        except TimeoutError:
            msg = f"{step.step_id} ({step.tool_name}) timed out after {self._timeout}s"
            logger.warning(msg)
            if step.optional:
                ctx.warnings.append(msg)
                return None
            ctx.errors.append(msg)
            return None
        except Exception as exc:
            msg = f"{step.step_id} ({step.tool_name}) failed: {exc}"
            logger.warning(msg)
            if step.optional:
                ctx.warnings.append(msg)
            else:
                ctx.errors.append(msg)
            return None

    @staticmethod
    def _deps_satisfied(step: InvestigationStep, executed: set[str]) -> bool:
        return all(dep in executed for dep in step.dependencies)
