from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db_copilot.api.deps import get_db_session
from db_copilot.correlation.repository import IncidentRepository
from db_copilot.domain.enums import IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models.incident import IncidentDetail, IncidentSummary

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=list[IncidentSummary])
async def list_incidents(
    severity: Severity | None = Query(None, description="Filter by incident severity"),
    incident_status: IncidentStatus | None = Query(
        None, alias="status", description="Filter by incident status"
    ),
    category: IncidentCategory | None = Query(None, description="Filter by incident category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> list[IncidentSummary]:
    """List incidents with filtering and pagination."""
    repo = IncidentRepository(db)
    return await repo.list_incidents(
        severity=severity,
        status=incident_status,
        category=category,
        limit=limit,
        offset=offset,
    )


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> IncidentDetail:
    """Retrieve full incident detail including evidence items and diagnosis."""
    repo = IncidentRepository(db)
    detail = await repo.get_incident_by_id(incident_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found",
        )
    return detail


@router.patch("/{incident_id}/resolve", response_model=IncidentSummary)
async def resolve_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> IncidentSummary:
    """Mark an incident as RESOLVED."""
    repo = IncidentRepository(db)
    updated = await repo.update_incident_status(incident_id, status=IncidentStatus.RESOLVED)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found",
        )
    await db.commit()
    return IncidentSummary(
        id=updated.id,
        database_id=updated.database_id,
        detected_at=updated.detected_at,
        resolved_at=updated.resolved_at,
        severity=updated.severity,
        category=updated.category,
        title=updated.title,
        status=updated.status,
    )
