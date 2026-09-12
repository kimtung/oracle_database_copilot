from db_copilot.correlation.graph import EvidenceGraph
from db_copilot.domain.enums import EvidenceType
from db_copilot.domain.models.diagnosis import Hypothesis
from db_copilot.domain.models.evidence import Evidence


class HypothesisDefinition:
    def __init__(
        self,
        code: str,
        name: str,
        description: str,
        direct_types: list[EvidenceType],
        correlating_types: list[EvidenceType],
    ):
        self.code = code
        self.name = name
        self.description = description
        self.direct_types = direct_types
        self.correlating_types = correlating_types


ROOT_HYPOTHESES: list[HypothesisDefinition] = [
    HypothesisDefinition(
        code="H1_PLAN_REGRESSION",
        name="H1: SQL Execution Plan Regression",
        description="Execution plan changed leading to inefficient table scans or join methods.",
        direct_types=[EvidenceType.SQL_PLAN_CHANGE],
        correlating_types=[EvidenceType.SQL_REGRESSION],
    ),
    HypothesisDefinition(
        code="H2_LOCK_CONTENTION",
        name="H2: Row/Table Lock Contention",
        description=(
            "Sessions are blocked waiting on row or transaction locks held by another session."
        ),
        direct_types=[EvidenceType.BLOCKING_SESSION],
        correlating_types=[EvidenceType.LONG_RUNNING_SESSION],
    ),
    HypothesisDefinition(
        code="H3_STATISTICS_STALE",
        name="H3: Stale Optimizer Statistics",
        description=(
            "Stale table or index statistics caused CBO to generate suboptimal execution plans."
        ),
        direct_types=[EvidenceType.STALE_STATISTICS, EvidenceType.CARDINALITY_MISMATCH],
        correlating_types=[EvidenceType.SQL_REGRESSION],
    ),
    HypothesisDefinition(
        code="H4_RESOURCE_EXHAUSTION",
        name="H4: Resource Capacity Exhaustion",
        description="Tablespace full, TEMP exhausted, or high CPU/memory starvation.",
        direct_types=[
            EvidenceType.TABLESPACE_FULL,
            EvidenceType.TEMP_FULL,
            EvidenceType.HIGH_CPU,
        ],
        correlating_types=[EvidenceType.JOB_FAILURE],
    ),
    HypothesisDefinition(
        code="H5_CODE_DEFECT",
        name="H5: Application Logic or Schema Defect",
        description="Failed batch jobs, invalid PL/SQL objects, or schema syntax/logic errors.",
        direct_types=[EvidenceType.JOB_FAILURE, EvidenceType.INVALID_OBJECTS],
        correlating_types=[EvidenceType.LONG_RUNNING_SESSION],
    ),
]


class HypothesisEngine:
    """
    Deterministic Hypothesis Ranking Engine.
    Evaluates observed evidence and causal graph topology against 5 standard root hypotheses.
    """

    def __init__(self, definitions: list[HypothesisDefinition] | None = None):
        self.definitions = definitions or ROOT_HYPOTHESES

    def calculate_confidence(
        self,
        h_def: HypothesisDefinition,
        evidences: list[Evidence],
        graph: EvidenceGraph | None = None,
    ) -> tuple[float, list[str]]:
        score = 0.0
        supporting: list[str] = []

        direct_count = 0
        correlating_count = 0

        for ev in evidences:
            ev_summary = f"{ev.type} on {ev.entity_type}:{ev.entity_id}"
            is_direct = False

            # Check explicit support tagging
            if h_def.code in ev.supports_hypothesis:
                is_direct = True

            # Check type matching
            if ev.type in h_def.direct_types:
                is_direct = True

            if is_direct:
                direct_count += 1
                score += 0.50
                supporting.append(f"Direct evidence: {ev_summary}")
            elif ev.type in h_def.correlating_types:
                correlating_count += 1
                score += 0.25
                supporting.append(f"Correlating evidence: {ev_summary}")

        # Bonus from graph causal chain validation
        if graph and (direct_count > 0 or correlating_count > 0):
            root_causes = graph.find_root_causes()
            chains = graph.find_causal_chains()

            has_graph_confirmation = False
            if h_def.code == "H2_LOCK_CONTENTION":
                has_graph_confirmation = any(
                    any(e.relation == "BLOCKS" for e in graph.adjacency.get(r.id, []))
                    for r in root_causes
                )
            elif h_def.code == "H1_PLAN_REGRESSION":
                has_graph_confirmation = any(
                    any(e.relation == "HAS_PLAN" for e in graph.adjacency.get(r.id, []))
                    for r in root_causes
                )
            elif h_def.code == "H4_RESOURCE_EXHAUSTION":
                has_graph_confirmation = any(
                    r.entity_type in ["TABLESPACE"] for r in root_causes
                )

            if has_graph_confirmation or len(chains) > 0:
                score += 0.20
                supporting.append("Causal graph topology confirms impact chain")

        # Clamp score between 0.0 and 1.0
        final_score = min(round(score, 2), 1.0)
        return final_score, supporting

    def rank_hypotheses(
        self,
        evidences: list[Evidence],
        graph: EvidenceGraph | None = None,
    ) -> list[Hypothesis]:
        """Rank and return all hypotheses matching the observed evidence."""
        results: list[Hypothesis] = []

        for h_def in self.definitions:
            confidence, supporting = self.calculate_confidence(h_def, evidences, graph)
            if confidence > 0.0:
                results.append(
                    Hypothesis(
                        name=h_def.name,
                        confidence=confidence,
                        supporting_evidence=supporting,
                        refuting_evidence=[],
                    )
                )

        # Sort descending by confidence score
        results.sort(key=lambda h: h.confidence, reverse=True)
        return results
