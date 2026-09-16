"""Tests for AIService — primary/fallback/rule-based logic."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.interfaces.llm_provider import LLMDiagnosisError
from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.domain.models.evidence import Evidence, EvidencePackage


def _make_settings(**overrides):
    from db_copilot.config.settings import Settings
    defaults = {
        "llm_provider": "gemini",
        "llm_fallback_provider": "openai",
        "gemini_api_key": "fake-gemini-key",
        "openai_api_key": "fake-openai-key",
        "claude_api_key": "",
        "llm_diagnosis_timeout": 5.0,
    }
    defaults.update(overrides)
    return Settings.model_validate(defaults)


def _make_package():
    return EvidencePackage(
        question="Test question",
        database_name="ORCL",
        evidence=[
            Evidence(
                type=EvidenceType.SQL_REGRESSION,
                entity_type="SQL",
                entity_id="aaa111",
                severity=Severity.HIGH,
                data={"ratio": 4.0},
            )
        ],
    )


def _make_diagnosis(confidence: float = 0.8) -> DiagnosisResult:
    return DiagnosisResult(
        diagnosis="Test diagnosis",
        confidence=confidence,
        primary_cause="SQL plan regression",
        evidence_used=["sql_regression: aaa111"],
        confidence_explanation="Strong evidence",
    )


class TestAIServiceDiagnosis:
    @pytest.mark.asyncio
    async def test_primary_provider_success(self):
        from db_copilot.ai.service import AIService

        settings = _make_settings()
        svc = AIService(settings)

        mock_provider = AsyncMock()
        mock_provider.diagnose = AsyncMock(return_value=_make_diagnosis(0.8))
        svc._primary = mock_provider

        result = await svc.diagnose(_make_package())
        assert result.confidence == pytest.approx(0.8)
        mock_provider.diagnose.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_when_primary_fails(self):
        from db_copilot.ai.service import AIService

        settings = _make_settings()
        svc = AIService(settings)

        primary = AsyncMock()
        primary.diagnose = AsyncMock(side_effect=LLMDiagnosisError("primary down"))
        fallback = AsyncMock()
        fallback.diagnose = AsyncMock(return_value=_make_diagnosis(0.6))

        svc._primary = primary
        svc._fallback = fallback

        result = await svc.diagnose(_make_package())
        assert result.confidence == pytest.approx(0.6)
        fallback.diagnose.assert_called_once()

    @pytest.mark.asyncio
    async def test_rule_based_fallback_when_all_fail(self):
        from db_copilot.ai.service import AIService

        settings = _make_settings()
        svc = AIService(settings)

        primary = AsyncMock()
        primary.diagnose = AsyncMock(side_effect=LLMDiagnosisError("primary down"))
        fallback = AsyncMock()
        fallback.diagnose = AsyncMock(side_effect=LLMDiagnosisError("fallback down"))

        svc._primary = primary
        svc._fallback = fallback

        result = await svc.diagnose(_make_package())
        # Should return rule-based diagnosis, not raise
        assert isinstance(result, DiagnosisResult)
        assert len(result.recommendations) >= 1
        assert "manually" in result.recommendations[0].note.lower()

    @pytest.mark.asyncio
    async def test_timeout_triggers_fallback(self):
        from db_copilot.ai.service import AIService

        settings = _make_settings()
        svc = AIService(settings)
        svc._timeout = 0.01  # 10ms — force timeout

        async def slow_diagnose(pkg):
            await asyncio.sleep(10)
            return _make_diagnosis()

        primary = AsyncMock()
        primary.diagnose = slow_diagnose
        fallback = AsyncMock()
        fallback.diagnose = AsyncMock(return_value=_make_diagnosis(0.5))

        svc._primary = primary
        svc._fallback = fallback

        result = await svc.diagnose(_make_package())
        assert result.confidence == pytest.approx(0.5)


class TestAIServiceIntentParsing:
    @pytest.mark.asyncio
    async def test_parse_intent_fallback_when_no_provider(self):
        from db_copilot.ai.service import AIService

        settings = _make_settings()
        svc = AIService(settings)
        # Simulate no working provider
        svc._primary = None
        svc._fallback = None

        result = await svc.parse_intent("General health check")
        assert result["intent_type"] == "GENERAL_HEALTH"
