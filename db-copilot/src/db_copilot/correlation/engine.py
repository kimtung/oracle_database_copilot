from __future__ import annotations

import logging
from typing import Any

from db_copilot.config.settings import Settings, get_settings
from db_copilot.correlation.graph import EvidenceGraph
from db_copilot.correlation.hypothesis_engine import HypothesisEngine
from db_copilot.correlation.repository import IncidentRepository
from db_copilot.correlation.rules.base import BaseRule
from db_copilot.correlation.rules.session_rules import (
    BlockingSessionRule,
    LongRunningSessionRule,
)
from db_copilot.correlation.rules.sql_rules import SqlRegressionRule
from db_copilot.correlation.rules.storage_rules import (
    InvalidObjectRule,
    JobFailureRule,
    TablespaceThresholdRule,
)
from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.domain.models.incident import Incident
from db_copilot.mcp.client import OracleMcpClient

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Correlation Engine Orchestrator.
    Coordinates rule evaluation, deduplication, causal graph generation,
    initial hypothesis ranking, and incident lifecycle persistence.
    """

    def __init__(
        self,
        repository: IncidentRepository,
        mcp_client: OracleMcpClient | None = None,
        rules: list[BaseRule] | None = None,
        hypothesis_engine: HypothesisEngine | None = None,
        settings: Settings | None = None,
    ):
        self.repo = repository
        self.mcp = mcp_client or OracleMcpClient()
        self.settings = settings or get_settings()
        self.hypothesis_engine = hypothesis_engine or HypothesisEngine()

        if rules is not None:
            self.rules = rules
        else:
            self.rules = [
                SqlRegressionRule(mcp_client=self.mcp, settings=self.settings),
                BlockingSessionRule(settings=self.settings),
                LongRunningSessionRule(settings=self.settings),
                TablespaceThresholdRule(settings=self.settings),
                JobFailureRule(settings=self.settings),
                InvalidObjectRule(settings=self.settings),
            ]

    async def correlate(
        self,
        collected_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> list[Incident]:
        """
        Evaluate raw collected metrics through all detection rules,
        correlate with existing open incidents, rank initial root cause hypotheses,
        and persist/update incident entities.
        """
        context = context or {}
        candidate_incidents: list[Incident] = []

        # 1. Map data slices to specific rules
        rule_data_mapping = {
            "SqlRegressionRule": collected_data.get("sql_metrics", []),
            "BlockingSessionRule": collected_data.get("blocking_sessions", []),
            "LongRunningSessionRule": collected_data.get("active_sessions", []),
            "TablespaceThresholdRule": collected_data.get("tablespaces", []),
            "JobFailureRule": collected_data.get("failed_jobs", []),
            "InvalidObjectRule": collected_data.get("invalid_objects", []),
        }

        for rule in self.rules:
            data_slice = rule_data_mapping.get(rule.name)
            if not data_slice:
                continue

            try:
                detected = await rule.evaluate(data_slice, context=context)
                candidate_incidents.extend(detected)
            except Exception as exc:
                logger.error(f"Detection rule '{rule.name}' failed: {exc}", exc_info=True)

        # 2. Process, deduplicate, and correlate candidate incidents
        processed_incidents: list[Incident] = []

        for candidate in candidate_incidents:
            # Determine primary entity_id
            entity_id = ""
            if candidate.evidence:
                entity_id = candidate.evidence[0].entity_id

            # Deduplication check: check if an open incident exists for this entity
            existing = None
            if entity_id:
                existing = await self.repo.find_open_incident(
                    candidate.category, entity_id, within_minutes=60
                )

            if existing:
                # Deduplication hit: Link new evidence to existing incident
                for ev in candidate.evidence:
                    await self.repo.attach_evidence_to_incident(existing.id, ev.id)
                logger.info(
                    f"Correlated evidence to existing incident {existing.id} ({candidate.category})"
                )
                processed_incidents.append(existing)
            else:
                # Brand new incident: Build graph and rank initial hypotheses
                graph = EvidenceGraph.build_from_evidences(candidate.evidence)
                ranked_hypotheses = self.hypothesis_engine.rank_hypotheses(
                    candidate.evidence, graph=graph
                )

                if ranked_hypotheses:
                    top_h = ranked_hypotheses[0]
                    candidate.diagnosis = DiagnosisResult(
                        diagnosis=f"Preliminary deterministic diagnosis: {top_h.name}",
                        confidence=top_h.confidence,
                        primary_cause=top_h.name,
                        evidence_used=top_h.supporting_evidence,
                        hypothesis_ranking=ranked_hypotheses,
                    )

                created = await self.repo.create_incident(candidate)
                logger.info(f"Created new incident {created.id}: {created.title}")
                processed_incidents.append(created)

        return processed_incidents
