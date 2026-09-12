from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db_copilot.db.schema import (
    EvidenceItem,
)
from db_copilot.db.schema import (
    Incident as SchemaIncident,
)
from db_copilot.domain.enums import (
    EvidenceType,
    IncidentCategory,
    IncidentStatus,
    Severity,
)
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import (
    Incident,
    IncidentDetail,
    IncidentSummary,
)


class IncidentRepository:
    """PostgreSQL repository for Incidents and correlation lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain_evidence(self, item: EvidenceItem) -> Evidence:
        try:
            type_val = EvidenceType(item.type) if item.type else EvidenceType.SQL_REGRESSION
        except (ValueError, TypeError):
            type_val = EvidenceType.SQL_REGRESSION

        try:
            severity_val = Severity(item.severity) if item.severity else Severity.INFO
        except (ValueError, TypeError):
            severity_val = Severity.INFO

        supports = []
        if isinstance(item.data, dict) and "supports_hypothesis" in item.data:
            supports = item.data["supports_hypothesis"]

        return Evidence(
            id=item.id,
            incident_id=item.incident_id,
            type=type_val,
            source=item.source or "",
            timestamp=item.timestamp or datetime.now(UTC),
            entity_type=item.entity_type or "",
            entity_id=item.entity_id or "",
            severity=severity_val,
            data=item.data or {},
            supports_hypothesis=supports,
        )

    def _to_domain_incident(
        self, schema_obj: SchemaIncident, evidence_list: list[Evidence] | None = None
    ) -> Incident:
        try:
            sev = Severity(schema_obj.severity) if schema_obj.severity else Severity.MEDIUM
        except (ValueError, TypeError):
            sev = Severity.MEDIUM

        try:
            cat = (
                IncidentCategory(schema_obj.category)
                if schema_obj.category
                else IncidentCategory.SQL_REGRESSION
            )
        except (ValueError, TypeError):
            cat = IncidentCategory.SQL_REGRESSION

        try:
            status = (
                IncidentStatus(schema_obj.status)
                if schema_obj.status
                else IncidentStatus.OPEN
            )
        except (ValueError, TypeError):
            status = IncidentStatus.OPEN

        ev_list = evidence_list
        if ev_list is None:
            ev_list = [self._to_domain_evidence(it) for it in (schema_obj.evidence_items or [])]

        diag = None
        if schema_obj.diagnosis and isinstance(schema_obj.diagnosis, dict):
            try:
                from db_copilot.domain.models.diagnosis import DiagnosisResult

                diag = DiagnosisResult.model_validate(schema_obj.diagnosis)
            except Exception:
                diag = None

        return Incident(
            id=schema_obj.id,
            database_id=schema_obj.database_id,
            detected_at=schema_obj.detected_at,
            resolved_at=schema_obj.resolved_at,
            severity=sev,
            category=cat,
            title=schema_obj.title,
            description=schema_obj.description or "",
            evidence=ev_list,
            diagnosis=diag,
            status=status,
        )

    async def create_incident(self, incident: Incident) -> Incident:
        """Create a new incident and link its initial evidence items."""
        sev_str = (
            incident.severity.value
            if hasattr(incident.severity, "value")
            else str(incident.severity)
        )
        cat_str = (
            incident.category.value
            if hasattr(incident.category, "value")
            else str(incident.category)
        )
        status_str = (
            incident.status.value
            if hasattr(incident.status, "value")
            else str(incident.status)
        )

        schema_incident = SchemaIncident(
            id=incident.id,
            database_id=incident.database_id,
            detected_at=incident.detected_at,
            resolved_at=incident.resolved_at,
            severity=sev_str,
            category=cat_str,
            title=incident.title,
            description=incident.description,
            status=status_str,
            diagnosis=incident.diagnosis.model_dump(mode="json") if incident.diagnosis else None,
        )
        self.session.add(schema_incident)

        # Attach any pre-existing or accompanying evidence
        saved_evidences: list[Evidence] = []
        for ev in incident.evidence:
            ev_item = EvidenceItem(
                id=ev.id,
                incident_id=schema_incident.id,
                type=ev.type.value if hasattr(ev.type, "value") else str(ev.type),
                source=ev.source,
                timestamp=ev.timestamp,
                entity_type=ev.entity_type,
                entity_id=ev.entity_id,
                severity=ev.severity.value if hasattr(ev.severity, "value") else str(ev.severity),
                data=ev.data,
            )
            self.session.add(ev_item)
            saved_evidences.append(ev)

        await self.session.flush()
        return self._to_domain_incident(schema_incident, evidence_list=saved_evidences)

    async def get_incident_by_id(self, incident_id: uuid.UUID) -> IncidentDetail | None:
        """Retrieve full incident detail including all linked evidence."""
        stmt = (
            select(SchemaIncident)
            .options(selectinload(SchemaIncident.evidence_items))
            .where(SchemaIncident.id == incident_id)
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return None

        domain_incident = self._to_domain_incident(obj)
        return IncidentDetail(
            incident=domain_incident,
            evidence=domain_incident.evidence,
            diagnosis=domain_incident.diagnosis,
        )

    async def list_incidents(
        self,
        severity: Severity | str | None = None,
        status: IncidentStatus | str | None = None,
        category: IncidentCategory | str | None = None,
        database_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[IncidentSummary]:
        """List incidents with filtering and pagination."""
        stmt = select(SchemaIncident)

        if database_id is not None:
            stmt = stmt.where(SchemaIncident.database_id == database_id)
        if severity is not None:
            sev_str = severity.value if hasattr(severity, "value") else str(severity)
            stmt = stmt.where(SchemaIncident.severity == sev_str)
        if status is not None:
            st_str = status.value if hasattr(status, "value") else str(status)
            stmt = stmt.where(SchemaIncident.status == st_str)
        if category is not None:
            cat_str = category.value if hasattr(category, "value") else str(category)
            stmt = stmt.where(SchemaIncident.category == cat_str)

        stmt = stmt.order_by(desc(SchemaIncident.detected_at)).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        items = res.scalars().all()

        summaries: list[IncidentSummary] = []
        for obj in items:
            try:
                sev = Severity(obj.severity) if obj.severity else Severity.MEDIUM
            except (ValueError, TypeError):
                sev = Severity.MEDIUM

            try:
                cat = (
                    IncidentCategory(obj.category)
                    if obj.category
                    else IncidentCategory.SQL_REGRESSION
                )
            except (ValueError, TypeError):
                cat = IncidentCategory.SQL_REGRESSION

            try:
                st = IncidentStatus(obj.status) if obj.status else IncidentStatus.OPEN
            except (ValueError, TypeError):
                st = IncidentStatus.OPEN

            summaries.append(
                IncidentSummary(
                    id=obj.id,
                    database_id=obj.database_id,
                    detected_at=obj.detected_at,
                    resolved_at=obj.resolved_at,
                    severity=sev,
                    category=cat,
                    title=obj.title,
                    status=st,
                )
            )
        return summaries

    async def update_incident_status(
        self,
        incident_id: uuid.UUID,
        status: IncidentStatus | str,
        resolved_at: datetime | None = None,
    ) -> Incident | None:
        """Update the status of an incident (e.g. to INVESTIGATING or RESOLVED)."""
        stmt = (
            select(SchemaIncident)
            .options(selectinload(SchemaIncident.evidence_items))
            .where(SchemaIncident.id == incident_id)
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return None

        status_str = status.value if hasattr(status, "value") else str(status)
        obj.status = status_str
        if status_str == IncidentStatus.RESOLVED.value or status == IncidentStatus.RESOLVED:
            obj.resolved_at = resolved_at or datetime.now(UTC)
        elif status_str == IncidentStatus.OPEN.value:
            obj.resolved_at = None

        await self.session.flush()
        return self._to_domain_incident(obj)

    async def attach_evidence_to_incident(
        self, incident_id: uuid.UUID, evidence_id: uuid.UUID
    ) -> bool:
        """Link an existing evidence item to an incident."""
        stmt = select(EvidenceItem).where(EvidenceItem.id == evidence_id)
        res = await self.session.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            return False

        item.incident_id = incident_id
        await self.session.flush()
        return True

    async def find_open_incident(
        self,
        category: IncidentCategory | str,
        entity_id: str,
        within_minutes: int = 60,
    ) -> Incident | None:
        """
        Deduplication helper: Find an open or investigating incident for the same category
        and entity within the time window.
        """
        cat_str = category.value if hasattr(category, "value") else str(category)
        cutoff = datetime.now(UTC) - timedelta(minutes=within_minutes)
        active_statuses = [IncidentStatus.OPEN.value, IncidentStatus.INVESTIGATING.value]

        # Query 1: Joined with EvidenceItem matching entity_id
        stmt = (
            select(SchemaIncident)
            .join(EvidenceItem, EvidenceItem.incident_id == SchemaIncident.id)
            .options(selectinload(SchemaIncident.evidence_items))
            .where(
                SchemaIncident.category == cat_str,
                SchemaIncident.status.in_(active_statuses),
                EvidenceItem.entity_id == entity_id,
                SchemaIncident.detected_at >= cutoff,
            )
            .order_by(desc(SchemaIncident.detected_at))
        )
        res = await self.session.execute(stmt)
        match = res.scalars().first()
        if match:
            return self._to_domain_incident(match)

        # Query 2: Fallback to title/description matching entity_id
        filter_text = (
            SchemaIncident.description.contains(entity_id)
            | SchemaIncident.title.contains(entity_id)
        )
        stmt_fallback = (
            select(SchemaIncident)
            .options(selectinload(SchemaIncident.evidence_items))
            .where(
                SchemaIncident.category == cat_str,
                SchemaIncident.status.in_(active_statuses),
                filter_text,
                SchemaIncident.detected_at >= cutoff,
            )
            .order_by(desc(SchemaIncident.detected_at))
        )
        res_fallback = await self.session.execute(stmt_fallback)
        fallback_match = res_fallback.scalars().first()
        if fallback_match:
            return self._to_domain_incident(fallback_match)

        return None
