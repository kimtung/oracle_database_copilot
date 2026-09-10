from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from db_copilot.domain.enums import EvidenceType, Severity


class Evidence(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    incident_id: UUID | None = None
    type: EvidenceType
    source: str = ""  # "DBA_HIST_SQLSTAT", "V$SESSION", etc.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    entity_type: str = ""  # "SQL", "SESSION", "TABLE", "PROCEDURE"
    entity_id: str = ""  # sql_id, session_id, object_name
    severity: Severity = Severity.INFO
    data: dict[str, Any] = Field(default_factory=dict)
    supports_hypothesis: list[str] = Field(default_factory=list)


class EvidencePackage(BaseModel):
    incident_id: UUID | None = None
    database_id: UUID | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
