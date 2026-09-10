from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from db_copilot.domain.enums import IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models.diagnosis import DiagnosisResult
from db_copilot.domain.models.evidence import Evidence


class Incident(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    database_id: UUID | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    severity: Severity = Severity.MEDIUM
    category: IncidentCategory
    title: str
    description: str = ""
    evidence: list[Evidence] = Field(default_factory=list)
    diagnosis: DiagnosisResult | None = None
    status: IncidentStatus = IncidentStatus.OPEN


class IncidentSummary(BaseModel):
    id: UUID
    database_id: UUID | None = None
    detected_at: datetime
    resolved_at: datetime | None = None
    severity: Severity
    category: IncidentCategory
    title: str
    status: IncidentStatus


class IncidentDetail(BaseModel):
    incident: Incident
    evidence: list[Evidence] = Field(default_factory=list)
    diagnosis: DiagnosisResult | None = None
