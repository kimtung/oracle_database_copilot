"""API routes for daily health report retrieval."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from db_copilot.api.deps import get_db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily")
async def get_latest_daily_report() -> dict:
    """Return the most recent daily health report."""
    async for session in get_db_session():
        result = await session.execute(
            text(
                """
                SELECT id, report_date, health_score, narrative,
                       critical_count, warning_count, info_count,
                       resolved_count, incidents_json, created_at
                FROM daily_reports
                ORDER BY report_date DESC
                LIMIT 1
                """
            )
        )
        row = result.mappings().first()
        if row is None:
            raise HTTPException(status_code=404, detail="No daily report available yet")
        return dict(row)


@router.get("/daily/{report_date}")
async def get_daily_report_by_date(report_date: date) -> dict:
    """Return the daily health report for a specific date (YYYY-MM-DD)."""
    async for session in get_db_session():
        result = await session.execute(
            text(
                """
                SELECT id, report_date, health_score, narrative,
                       critical_count, warning_count, info_count,
                       resolved_count, incidents_json, created_at
                FROM daily_reports
                WHERE report_date = :report_date
                """
            ),
            {"report_date": report_date},
        )
        row = result.mappings().first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for {report_date}",
            )
        return dict(row)
