"""AIService — orchestrates LLM providers for diagnosis and reporting.

Handles provider selection, timeout, retry logic, and safe fallback
to rule-based diagnosis when all LLMs are unavailable.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime

from db_copilot.config.settings import Settings
from db_copilot.domain.interfaces.llm_provider import LLMDiagnosisError, LLMProvider
from db_copilot.domain.models.diagnosis import DiagnosisResult, Recommendation
from db_copilot.domain.models.evidence import EvidencePackage
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


def _create_provider(provider_name: str, settings: Settings) -> LLMProvider:
    """Factory: create LLM provider by name using settings credentials."""
    match provider_name.lower():
        case "gemini":
            from db_copilot.ai.providers.gemini_provider import GeminiProvider

            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
            )
        case "openai":
            from db_copilot.ai.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )
        case "claude":
            from db_copilot.ai.providers.claude_provider import ClaudeProvider

            return ClaudeProvider(
                api_key=settings.claude_api_key,
                model=settings.claude_model,
            )
        case _:
            raise ValueError(f"Unknown LLM provider: {provider_name!r}")


class AIService:
    """Orchestrates LLM calls with primary/fallback/rule-based safety net.

    Diagnosis flow:
      1. Try primary provider (with timeout).
      2. On timeout/error → try fallback provider.
      3. On both failing → synthesise DiagnosisResult from HypothesisEngine output.

    This ensures the system ALWAYS returns some diagnosis even when all LLMs
    are unavailable (e.g., no API keys configured, network down).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._primary: LLMProvider | None = None
        self._fallback: LLMProvider | None = None
        self._timeout = settings.llm_diagnosis_timeout

    # ── Public API ────────────────────────────────────────────────────────────

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """Return structured diagnosis for given evidence package.

        Never raises — always returns a DiagnosisResult.
        """
        primary = self._get_primary()
        if primary is not None:
            try:
                return await asyncio.wait_for(primary.diagnose(package), timeout=self._timeout)
            except TimeoutError:
                logger.warning(
                    "Primary LLM provider timed out after %.0fs, trying fallback",
                    self._timeout,
                )
            except (LLMDiagnosisError, Exception) as exc:
                logger.warning("Primary LLM provider failed: %s", exc)

        fallback = self._get_fallback()
        if fallback is not None and fallback is not primary:
            try:
                return await asyncio.wait_for(
                    fallback.diagnose(package), timeout=self._timeout
                )
            except (TimeoutError, LLMDiagnosisError, Exception) as exc:
                logger.warning("Fallback LLM provider also failed: %s", exc)

        logger.error(
            "All LLM providers failed; generating rule-based fallback diagnosis"
        )
        return self._rule_based_diagnosis(package)

    async def parse_intent(self, question: str) -> dict:
        """Parse natural language question into InvestigationIntent dict."""
        now = datetime.now(UTC)
        primary = self._get_primary()
        if primary is not None:
            try:
                return await asyncio.wait_for(
                    primary.parse_intent(question, now), timeout=10.0
                )
            except Exception as exc:
                logger.warning("Intent parsing failed: %s", exc)
        return {
            "intent_type": "GENERAL_HEALTH",
            "entity_type": "DATABASE",
            "entity_id": "",
            "start_time": "",
            "end_time": "",
            "focus_metric": "general",
        }

    async def generate_daily_report(
        self,
        incidents: list[Incident],
        database_name: str,
        report_date: date,
    ) -> tuple[int, str]:
        """Generate daily health report narrative and return (health_score, markdown_text)."""
        health_score = self._calc_health_score(incidents)
        primary = self._get_primary()
        if primary is not None:
            try:
                narrative = await asyncio.wait_for(
                    primary.generate_report_section(incidents, "full_report"),
                    timeout=60.0,
                )
                return health_score, narrative
            except Exception as exc:
                logger.warning("Daily report LLM generation failed: %s", exc)

        # Fallback: simple deterministic report
        narrative = self._rule_based_report(incidents, database_name, report_date, health_score)
        return health_score, narrative

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_primary(self) -> LLMProvider | None:
        has_key = (
            self._settings.gemini_api_key
            or self._settings.openai_api_key
            or self._settings.claude_api_key
        )
        if self._primary is None and has_key:
            try:
                self._primary = _create_provider(
                    self._settings.llm_provider, self._settings
                )
            except Exception as exc:
                logger.error("Failed to create primary LLM provider: %s", exc)
        return self._primary

    def _get_fallback(self) -> LLMProvider | None:
        if self._fallback is None:
            try:
                if self._settings.llm_fallback_provider != self._settings.llm_provider:
                    self._fallback = _create_provider(
                        self._settings.llm_fallback_provider, self._settings
                    )
            except Exception as exc:
                logger.warning("Failed to create fallback LLM provider: %s", exc)
        return self._fallback

    @staticmethod
    def _rule_based_diagnosis(package: EvidencePackage) -> DiagnosisResult:
        """Synthesize diagnosis from HypothesisEngine hypotheses only (no LLM)."""
        hypotheses = package.hypotheses or []
        top = hypotheses[0] if hypotheses else None

        if top is not None and hasattr(top, "name"):
            primary_cause = top.name
            confidence = getattr(top, "confidence", 0.3)
            diagnosis = f"Rule-based diagnosis: {primary_cause}"
        else:
            primary_cause = "Unknown — insufficient evidence"
            confidence = 0.0
            diagnosis = "Unable to determine root cause. Manual DBA review required."

        return DiagnosisResult(
            diagnosis=diagnosis,
            confidence=confidence,
            primary_cause=primary_cause,
            evidence_used=[e.type.value for e in package.evidence[:5]],
            evidence_against=[],
            recommendations=[
                Recommendation(
                    action="Review the collected evidence manually",
                    rationale="AI diagnosis is currently unavailable",
                    risk="LOW",
                    sql=None,
                    priority="HIGH",
                    note="DBA must review and execute manually. AI service offline.",
                )
            ],
            confidence_explanation=(
                "Diagnosis based on deterministic rule engine only (AI unavailable)."
            ),
            alternative_causes=[],
        )

    @staticmethod
    def _rule_based_report(
        incidents: list[Incident],
        database_name: str,
        report_date: date,
        health_score: int,
    ) -> str:
        critical = [i for i in incidents if i.severity.value == "CRITICAL"]
        high = [i for i in incidents if i.severity.value == "HIGH"]
        medium = [i for i in incidents if i.severity.value == "MEDIUM"]

        lines = [
            f"# Oracle DB Health Report — {report_date}",
            f"**Database:** {database_name}",
            f"**Health Score:** {health_score}/100",
            "",
            f"## Critical Issues ({len(critical)})",
        ]
        for inc in critical:
            lines.append(f"- **{inc.title}** ({inc.category.value})")

        lines += [f"\n## Warnings ({len(high) + len(medium)})"]
        for inc in high + medium:
            lines.append(f"- {inc.title} ({inc.severity.value})")

        lines += [
            "",
            "## NOTE",
            "No automatic database changes were executed by this system.",
            "_Report generated by rule engine — AI service was unavailable._",
        ]
        return "\n".join(lines)

    @staticmethod
    def _calc_health_score(incidents: list[Incident]) -> int:
        score = 100
        for inc in incidents:
            sev = inc.severity.value
            if sev == "CRITICAL":
                score -= 20
            elif sev == "HIGH":
                score -= 10
            elif sev == "MEDIUM":
                score -= 5
        return max(0, score)
