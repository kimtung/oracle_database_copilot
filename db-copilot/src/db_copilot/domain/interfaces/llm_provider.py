from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.domain.models.evidence import EvidencePackage
from db_copilot.domain.models.incident import Incident


class LLMDiagnosisError(Exception):
    """Raised when LLM cannot produce a valid structured diagnosis."""


class LLMProvider(ABC):
    """Abstract interface for LLM backend providers.

    All implementations must produce structured output only.
    No free-form text, no Oracle credentials in prompts.
    """

    @abstractmethod
    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        """Analyze evidence package and return structured diagnosis.

        Must return DiagnosisResult (Pydantic model).
        Raise LLMDiagnosisError if valid JSON cannot be produced.
        Never include Oracle credentials, connection strings, or PII.
        """

    @abstractmethod
    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        """Parse natural-language DBA question into InvestigationIntent dict.

        Expected output keys: intent_type, entity_type, entity_id,
        time_range (start_time, end_time ISO strings), focus_metric.
        """

    @abstractmethod
    async def generate_report_section(
        self,
        incidents: list[Incident],
        section_type: str,
    ) -> str:
        """Generate a markdown section of the daily health report.

        section_type: 'full_report' | 'critical' | 'warning' | 'summary'
        Never recommend automatic execution of database commands.
        """
