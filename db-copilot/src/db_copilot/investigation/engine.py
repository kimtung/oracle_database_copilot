"""InvestigationEngine — end-to-end orchestrator for DBA question investigation.

Connects:
  IntentParser → InvestigationPlanner → InvestigationExecutor → EvidenceNormalizer
  → HypothesisEngine → EvidenceGraph → AIService → InvestigationResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from db_copilot.ai.service import AIService
from db_copilot.config.settings import Settings, get_settings
from db_copilot.correlation.hypothesis_engine import HypothesisEngine
from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.domain.models.evidence import Evidence, EvidencePackage
from db_copilot.investigation.context import InvestigationContext
from db_copilot.investigation.executor import InvestigationExecutor
from db_copilot.investigation.planner import (
    IntentParser,
    InvestigationIntent,
    InvestigationPlanner,
)
from db_copilot.investigation.source_mapper import SourceCodeMapper
from db_copilot.mcp.client import OracleMcpClient

logger = logging.getLogger(__name__)


@dataclass
class InvestigationResult:
    """Final output of a completed investigation."""

    id: UUID = field(default_factory=uuid4)
    question: str = ""
    intent: InvestigationIntent | None = None
    evidence: list[Evidence] = field(default_factory=list)
    diagnosis: DiagnosisResult | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
    step_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    status: str = "completed"  # "completed" | "partial" | "failed"


class InvestigationEngine:
    """Orchestrates end-to-end investigation of a natural-language DBA question."""

    def __init__(
        self,
        mcp_client: OracleMcpClient,
        ai_service: AIService,
        settings: Settings | None = None,
    ) -> None:
        self._mcp = mcp_client
        self._ai = ai_service
        self._settings = settings or get_settings()

        self._intent_parser = IntentParser()
        self._planner = InvestigationPlanner()
        self._hypothesis_engine = HypothesisEngine()
        self._executor = InvestigationExecutor(
            mcp_client=mcp_client,
            step_timeout=self._settings.investigation_step_timeout,
        )
        self._source_mapper = SourceCodeMapper(mcp_client)

    async def investigate(self, question: str, database_name: str = "") -> InvestigationResult:
        """Run full investigation pipeline for the given DBA question."""
        result = InvestigationResult(question=question)

        try:
            # 1. Parse intent
            intent = self._intent_parser.parse(question)
            result.intent = intent
            logger.info(
                "Investigation started: intent=%s entity=%s",
                intent.intent_type,
                intent.entity_id or "N/A",
            )

            # 2. Build investigation plan
            plan = self._planner.build_plan(intent)

            # 3. Execute steps via MCP
            ctx: InvestigationContext = await self._executor.execute(plan)
            result.step_count = len(ctx.step_results)
            result.warnings.extend(ctx.warnings)
            result.errors.extend(ctx.errors)

            # 4. Collect evidence from context (already in Evidence form from collectors)
            evidence_list: list[Evidence] = list(ctx.collected_evidence)

            # 6. Rank hypotheses using HypothesisEngine
            hypotheses = self._hypothesis_engine.rank_hypotheses(evidence_list)

            # 7. Optionally map source code for procedure investigations
            source_fragment: str | None = None
            if intent.entity_id and ctx.dynamic_parameters.get("step_1.top_sql_id"):
                try:
                    sf = await self._source_mapper.map_sql_to_source(
                        ctx.dynamic_parameters["step_1.top_sql_id"]
                    )
                    if sf:
                        source_fragment = sf.source
                except Exception as exc:
                    logger.debug("Source mapping skipped: %s", exc)

            # 8. Assemble EvidencePackage for LLM
            package = EvidencePackage(
                evidence=evidence_list,
                question=question,
                intent={
                    "intent_type": intent.intent_type.value,
                    "entity_id": intent.entity_id,
                },
                hypotheses=hypotheses,
                database_name=database_name,
                investigation_timestamp=result.started_at,
                source_fragment=source_fragment,
            )

            # 9. AI diagnosis
            diagnosis = await self._ai.diagnose(package)
            result.diagnosis = diagnosis

        except Exception as exc:
            logger.error("Investigation failed: %s", exc, exc_info=True)
            result.status = "failed"
            result.errors.append(str(exc))
        finally:
            result.completed_at = datetime.now(UTC)
            if result.started_at:
                result.duration_seconds = (
                    result.completed_at - result.started_at
                ).total_seconds()

        if result.errors and not result.diagnosis:
            result.status = "failed"
        elif result.warnings:
            result.status = "partial"

        logger.info(
            "Investigation completed: status=%s duration=%.1fs evidence=%d",
            result.status,
            result.duration_seconds,
            len(result.evidence),
        )
        return result
