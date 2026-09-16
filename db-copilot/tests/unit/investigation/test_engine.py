"""End-to-end test for InvestigationEngine with full mocking."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.investigation.engine import InvestigationEngine


def _make_settings():
    from db_copilot.config.settings import Settings
    return Settings(
        llm_provider="gemini",
        gemini_api_key="fake-key",
        investigation_step_timeout=5.0,
    )


class TestInvestigationEngine:
    @pytest.mark.asyncio
    async def test_investigate_general_health_returns_result(self):
        settings = _make_settings()

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(
            return_value={"db_name": "ORCL", "status": "OPEN"}
        )

        mock_ai = MagicMock()
        mock_ai.diagnose = AsyncMock(
            return_value=DiagnosisResult(
                diagnosis="System healthy",
                confidence=0.9,
                primary_cause="No issues detected",
                evidence_used=[],
            )
        )

        engine = InvestigationEngine(
            mcp_client=mock_mcp,
            ai_service=mock_ai,
            settings=settings,
        )

        result = await engine.investigate("Show me a general health overview", "ORCL")

        assert result.question == "Show me a general health overview"
        assert result.status in ("completed", "partial")
        assert result.diagnosis is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_investigate_completes_even_when_mcp_fails(self):
        settings = _make_settings()

        mock_mcp = MagicMock()
        mock_mcp.call_tool = AsyncMock(side_effect=RuntimeError("MCP server down"))

        mock_ai = MagicMock()
        mock_ai.diagnose = AsyncMock(
            return_value=DiagnosisResult(
                diagnosis="Fallback diagnosis",
                confidence=0.3,
                primary_cause="Unable to collect evidence",
                evidence_used=[],
            )
        )

        engine = InvestigationEngine(
            mcp_client=mock_mcp,
            ai_service=mock_ai,
            settings=settings,
        )

        result = await engine.investigate("Why is the database slow?")

        # Should not raise — must always return a result
        assert result.completed_at is not None
        assert result.diagnosis is not None
