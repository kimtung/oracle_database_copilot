"""DailyReportService — generates and persists daily Oracle DB health reports."""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db_copilot.ai.service import AIService
from db_copilot.correlation.repository import IncidentRepository
from db_copilot.domain.enums import IncidentStatus
from db_copilot.domain.models.incident import Incident

logger = logging.getLogger(__name__)


class DailyReportService:
    """Generates daily health reports and saves them to the daily_reports table.

    Health score calculation (0-100):
      - Start at 100
      - CRITICAL incident: -20 points each
      - HIGH incident:     -10 points each
      - MEDIUM incident:   -5 points each
      - Minimum score:     0
    """

    def __init__(self, ai_service: AIService, incident_repo: IncidentRepository) -> None:
        self._ai = ai_service
        self._incidents = incident_repo

    async def generate_daily(
        self,
        session: AsyncSession,
        report_date: date | None = None,
        database_name: str = "Oracle DB",
    ) -> dict:
        """Generate and persist the daily health report.

        Returns a summary dict with health_score, incident counts, and narrative preview.
        """
        if report_date is None:
            report_date = datetime.now(UTC).date()

        logger.info("Generating daily report for %s", report_date)

        # Collect incidents from last 24 hours
        since = datetime.combine(report_date, datetime.min.time()).replace(tzinfo=UTC)
        until = since + timedelta(days=1)
        incidents = await self._incidents.list_incidents(
            session,
            since=since,
            until=until,
            limit=200,
        )

        # Calculate health score
        health_score = self._calc_health_score(incidents)

        # Generate AI narrative
        health_score, narrative = await self._ai.generate_daily_report(
            incidents=incidents,
            database_name=database_name,
            report_date=report_date,
        )

        # Count by severity
        critical = sum(1 for i in incidents if i.severity.value == "CRITICAL")
        high = sum(1 for i in incidents if i.severity.value == "HIGH")
        medium = sum(1 for i in incidents if i.severity.value == "MEDIUM")
        resolved = sum(1 for i in incidents if i.status == IncidentStatus.RESOLVED)

        # Persist to daily_reports table
        report_id = uuid4()
        await session.execute(
            text(
                """
                INSERT INTO daily_reports
                  (id, database_id, report_date, health_score, narrative,
                   critical_count, warning_count, info_count, resolved_count,
                   incidents_json, created_at)
                VALUES
                  (:id, NULL, :report_date, :health_score, :narrative,
                   :critical_count, :warning_count, :info_count, :resolved_count,
                   :incidents_json, :created_at)
                ON CONFLICT (report_date) DO UPDATE SET
                  health_score   = EXCLUDED.health_score,
                  narrative      = EXCLUDED.narrative,
                  critical_count = EXCLUDED.critical_count,
                  warning_count  = EXCLUDED.warning_count,
                  info_count     = EXCLUDED.info_count,
                  resolved_count = EXCLUDED.resolved_count,
                  incidents_json = EXCLUDED.incidents_json,
                  created_at     = EXCLUDED.created_at
                """
            ),
            {
                "id": str(report_id),
                "report_date": report_date,
                "health_score": health_score,
                "narrative": narrative,
                "critical_count": critical,
                "warning_count": high,
                "info_count": medium,
                "resolved_count": resolved,
                "incidents_json": json.dumps([str(i.id) for i in incidents]),
                "created_at": datetime.now(UTC),
            },
        )
        await session.commit()

        logger.info(
            "Daily report saved: date=%s score=%d critical=%d high=%d",
            report_date,
            health_score,
            critical,
            high,
        )
        return {
            "id": str(report_id),
            "report_date": report_date.isoformat(),
            "health_score": health_score,
            "critical_count": critical,
            "warning_count": high,
            "info_count": medium,
            "incident_count": len(incidents),
            "narrative_preview": narrative[:200] if narrative else "",
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
