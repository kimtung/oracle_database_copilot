"""Tests for DailyReportService — health score calculation and report generation."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from db_copilot.domain.enums import IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models.incident import Incident


def _make_incident(severity: str, status: str = "OPEN") -> Incident:
    return Incident(
        id=uuid4(),
        severity=Severity(severity),
        category=IncidentCategory.SQL_REGRESSION,
        title=f"Test incident {severity}",
        status=IncidentStatus(status),
    )


class TestDailyReportServiceHealthScore:
    def test_health_score_no_incidents(self):
        from db_copilot.application.report_service import DailyReportService
        svc = DailyReportService(ai_service=MagicMock(), incident_repo=MagicMock())
        score = svc._calc_health_score([])
        assert score == 100

    def test_health_score_one_critical(self):
        from db_copilot.application.report_service import DailyReportService
        svc = DailyReportService(ai_service=MagicMock(), incident_repo=MagicMock())
        incidents = [_make_incident("CRITICAL")]
        assert svc._calc_health_score(incidents) == 80

    def test_health_score_multiple_incidents(self):
        from db_copilot.application.report_service import DailyReportService
        svc = DailyReportService(ai_service=MagicMock(), incident_repo=MagicMock())
        incidents = [
            _make_incident("CRITICAL"),  # -20
            _make_incident("HIGH"),      # -10
            _make_incident("MEDIUM"),    # -5
        ]
        assert svc._calc_health_score(incidents) == 65

    def test_health_score_minimum_is_zero(self):
        from db_copilot.application.report_service import DailyReportService
        svc = DailyReportService(ai_service=MagicMock(), incident_repo=MagicMock())
        incidents = [_make_incident("CRITICAL")] * 10  # -200 -> floored at 0
        assert svc._calc_health_score(incidents) == 0

    @pytest.mark.asyncio
    async def test_generate_daily_no_incidents(self):
        from db_copilot.application.report_service import DailyReportService

        mock_ai = MagicMock()
        mock_ai.generate_daily_report = AsyncMock(return_value=(100, "# All clear"))

        mock_repo = MagicMock()
        mock_repo.list_incidents = AsyncMock(return_value=[])

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock())
        mock_session.commit = AsyncMock()

        svc = DailyReportService(ai_service=mock_ai, incident_repo=mock_repo)
        result = await svc.generate_daily(mock_session, report_date=date(2026, 9, 16))

        assert result["health_score"] == 100
        assert result["critical_count"] == 0
        assert result["incident_count"] == 0
