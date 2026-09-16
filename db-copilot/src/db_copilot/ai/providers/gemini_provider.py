"""Google Gemini LLM provider implementation."""

from __future__ import annotations

import json
import logging
from datetime import datetime

from db_copilot.ai.prompts.diagnosis_prompt import (
    DIAGNOSIS_SYSTEM_PROMPT,
    DIAGNOSIS_USER_TEMPLATE,
    INTENT_SYSTEM_PROMPT,
)
from db_copilot.ai.prompts.report_prompt import REPORT_SYSTEM_PROMPT, REPORT_USER_TEMPLATE
from db_copilot.domain.interfaces.llm_provider import LLMDiagnosisError, LLMProvider
from db_copilot.domain.models.diagnosis import DiagnosisResult, Hypothesis, Recommendation
from db_copilot.domain.models.evidence import EvidencePackage
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini provider using google-genai SDK.

    All SDK imports are lazy to allow mocking in tests.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model = model

    def _get_client(self):  # type: ignore[no-untyped-def]
        from google import genai  # lazy import for testability
        return genai.Client(api_key=self._api_key)

    def _get_config(self, mime: str = "application/json", temp: float = 0.1):  # type: ignore[no-untyped-def]
        from google.genai import types  # lazy import
        return types.GenerateContentConfig(response_mime_type=mime, temperature=temp)

    async def diagnose(self, package: EvidencePackage) -> DiagnosisResult:
        user_prompt = DIAGNOSIS_USER_TEMPLATE.format(
            question=package.question or "General database performance investigation",
            database_name=package.database_name or "unknown",
            timestamp=(
                package.investigation_timestamp.isoformat()
                if package.investigation_timestamp
                else datetime.utcnow().isoformat()
            ),
            hypotheses_json=json.dumps(
                [h.model_dump() for h in (package.hypotheses or [])], indent=2
            ),
            evidence_json=json.dumps(
                [self._serialize_evidence(e) for e in package.evidence], indent=2
            ),
            context_json=json.dumps(
                {
                    "sql_details": package.sql_details,
                    "source_fragment": package.source_fragment,
                    "baseline_data": package.baseline_data,
                },
                indent=2,
            ),
        )
        full_prompt = f"{DIAGNOSIS_SYSTEM_PROMPT}\n\n{user_prompt}"
        try:
            client = self._get_client()
            config = self._get_config("application/json", 0.1)
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=full_prompt,
                config=config,
            )
            return self._parse_diagnosis(response.text)
        except LLMDiagnosisError:
            raise
        except Exception as exc:
            logger.error("Gemini diagnosis failed: %s", exc, exc_info=True)
            raise LLMDiagnosisError(f"Gemini error: {exc}") from exc

    async def parse_intent(self, question: str, current_time: datetime) -> dict:
        prompt = (
            f"{INTENT_SYSTEM_PROMPT}\n\n"
            f"Current time: {current_time.isoformat()}\n"
            f"Question: {question}"
        )
        try:
            client = self._get_client()
            config = self._get_config("application/json", 0.0)
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            return json.loads(response.text)
        except Exception as exc:
            logger.warning("Gemini intent parse failed: %s", exc)
            return {
                "intent_type": "GENERAL_HEALTH",
                "entity_type": "DATABASE",
                "entity_id": "",
            }

    async def generate_report_section(
        self, incidents: list[Incident], section_type: str
    ) -> str:
        incidents_json = json.dumps(
            [self._serialize_incident(i) for i in incidents], indent=2
        )
        prompt = REPORT_USER_TEMPLATE.format(
            database_name="Oracle DB",
            report_date=datetime.utcnow().strftime("%Y-%m-%d"),
            health_score=self._calc_health_score(incidents),
            incidents_json=incidents_json,
            metrics_json="{}",
        )
        try:
            client = self._get_client()
            config = self._get_config("text/plain", 0.3)
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=f"{REPORT_SYSTEM_PROMPT}\n\n{prompt}",
                config=config,
            )
            return response.text
        except Exception as exc:
            logger.error("Gemini report generation failed: %s", exc)
            return f"# Daily Report\n\nReport generation failed: {exc}"

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _parse_diagnosis(self, raw_json: str) -> DiagnosisResult:
        try:
            data = json.loads(raw_json)
            recs = [
                Recommendation(**r) if isinstance(r, dict) else r
                for r in data.get("recommendations", [])
            ]
            hyps = [
                Hypothesis(**h) if isinstance(h, dict) else h
                for h in data.get("hypothesis_ranking", [])
            ]
            return DiagnosisResult(
                diagnosis=data.get("diagnosis", ""),
                confidence=float(data.get("confidence", 0.0)),
                primary_cause=data.get("primary_cause", ""),
                evidence_used=data.get("evidence_used", []),
                evidence_against=data.get("evidence_against", []),
                recommendations=recs,
                confidence_explanation=data.get("confidence_explanation", ""),
                alternative_causes=data.get("alternative_causes", []),
                hypothesis_ranking=hyps,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise LLMDiagnosisError(f"Failed to parse Gemini JSON: {exc}") from exc

    @staticmethod
    def _serialize_evidence(e) -> dict:  # type: ignore[no-untyped-def]
        return {
            "type": e.type.value,
            "entity": f"{e.entity_type}:{e.entity_id}",
            "severity": e.severity.value,
            "data": e.data,
        }

    @staticmethod
    def _serialize_incident(i: Incident) -> dict:
        return {
            "id": str(i.id),
            "title": i.title,
            "severity": i.severity.value,
            "category": i.category.value,
            "status": i.status.value,
        }

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
