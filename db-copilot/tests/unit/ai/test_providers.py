"""Tests for LLM providers — all LLM SDK calls are mocked via _get_client."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.interfaces.llm_provider import LLMDiagnosisError
from db_copilot.domain.models.evidence import Evidence, EvidencePackage


def _make_package() -> EvidencePackage:
    return EvidencePackage(
        question="Why is PROC_SETTLEMENT slow?",
        database_name="ORCL",
        investigation_timestamp=datetime(2026, 9, 16, 6, 0, 0, tzinfo=UTC),
        evidence=[
            Evidence(
                type=EvidenceType.SQL_REGRESSION,
                entity_type="SQL",
                entity_id="abc123",
                severity=Severity.HIGH,
                data={"ratio": 5.2},
            )
        ],
    )


_VALID_DIAG_JSON = json.dumps({
    "diagnosis": "SQL plan regression detected",
    "confidence": 0.85,
    "primary_cause": "Execution plan changed from index scan to full table scan",
    "evidence_used": ["sql_regression: abc123"],
    "evidence_against": [],
    "recommendations": [
        {
            "action": "Gather statistics on ACCOUNT_POSITION table",
            "rationale": "Stale statistics may have caused plan change",
            "risk": "LOW",
            "sql": "EXEC DBMS_STATS.GATHER_TABLE_STATS(NULL, 'ACCOUNT_POSITION');",
            "priority": "HIGH",
            "note": "DBA must review and execute manually",
        }
    ],
    "confidence_explanation": (
        "Strong evidence of plan regression with 5.2x performance degradation"
    ),
    "alternative_causes": ["Resource pressure"],
    "hypothesis_ranking": [],
})


# ── Gemini Provider tests ─────────────────────────────────────────────────────

class TestGeminiProvider:
    @pytest.mark.asyncio
    async def test_diagnose_success(self):
        from db_copilot.ai.providers.gemini_provider import GeminiProvider

        mock_response = MagicMock()
        mock_response.text = _VALID_DIAG_JSON

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        provider = GeminiProvider(api_key="test-key")
        provider._get_client = lambda: mock_client
        provider._get_config = lambda mime="application/json", temp=0.1: MagicMock()

        result = await provider.diagnose(_make_package())

        assert result.confidence == pytest.approx(0.85)
        assert "plan regression" in result.diagnosis.lower()
        assert len(result.recommendations) == 1
        assert result.recommendations[0].priority == "HIGH"

    @pytest.mark.asyncio
    async def test_diagnose_bad_json_raises_error(self):
        from db_copilot.ai.providers.gemini_provider import GeminiProvider

        mock_response = MagicMock()
        mock_response.text = "not valid json {"

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        provider = GeminiProvider(api_key="test-key")
        provider._get_client = lambda: mock_client
        provider._get_config = lambda mime="application/json", temp=0.1: MagicMock()

        with pytest.raises(LLMDiagnosisError):
            await provider.diagnose(_make_package())

    @pytest.mark.asyncio
    async def test_parse_intent_success(self):
        from db_copilot.ai.providers.gemini_provider import GeminiProvider

        intent_json = json.dumps({
            "intent_type": "SLOW_PROCEDURE",
            "entity_id": "PROC_SETTLEMENT",
        })
        mock_response = MagicMock()
        mock_response.text = intent_json

        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        provider = GeminiProvider(api_key="test-key")
        provider._get_client = lambda: mock_client
        provider._get_config = lambda mime="application/json", temp=0.0: MagicMock()

        result = await provider.parse_intent(
            "Why is PROC_SETTLEMENT slow?", datetime.now()
        )
        assert result["intent_type"] == "SLOW_PROCEDURE"


# ── OpenAI Provider tests ─────────────────────────────────────────────────────

class TestOpenAIProvider:
    @pytest.mark.asyncio
    async def test_diagnose_success(self):
        from db_copilot.ai.providers.openai_provider import OpenAIProvider

        mock_message = MagicMock()
        mock_message.content = _VALID_DIAG_JSON
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(api_key="test-key")
        provider._get_client = lambda: mock_client

        result = await provider.diagnose(_make_package())
        assert result.confidence == pytest.approx(0.85)

    @pytest.mark.asyncio
    async def test_diagnose_api_error_raises(self):
        from db_copilot.ai.providers.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=RuntimeError("API unavailable")
        )

        provider = OpenAIProvider(api_key="test-key")
        provider._get_client = lambda: mock_client

        with pytest.raises(LLMDiagnosisError):
            await provider.diagnose(_make_package())


# ── Claude Provider tests ─────────────────────────────────────────────────────

class TestClaudeProvider:
    @pytest.mark.asyncio
    async def test_diagnose_success(self):
        from db_copilot.ai.providers.claude_provider import ClaudeProvider

        mock_content = MagicMock()
        mock_content.text = _VALID_DIAG_JSON
        mock_response = MagicMock()
        mock_response.content = [mock_content]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        provider = ClaudeProvider(api_key="test-key")
        provider._get_client = lambda: mock_client

        result = await provider.diagnose(_make_package())
        assert result.confidence == pytest.approx(0.85)

    @pytest.mark.asyncio
    async def test_diagnose_json_in_markdown_block(self):
        from db_copilot.ai.providers.claude_provider import ClaudeProvider

        mock_content = MagicMock()
        mock_content.text = f"```json\n{_VALID_DIAG_JSON}\n```"
        mock_response = MagicMock()
        mock_response.content = [mock_content]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        provider = ClaudeProvider(api_key="test-key")
        provider._get_client = lambda: mock_client

        result = await provider.diagnose(_make_package())
        assert result.primary_cause != ""
