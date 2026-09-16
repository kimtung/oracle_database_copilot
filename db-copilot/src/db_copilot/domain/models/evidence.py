from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from db_copilot.domain.enums import EvidenceType, Severity

if TYPE_CHECKING:
    pass


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
    """Container passed to LLM for diagnosis.

    Never include Oracle credentials, connection strings, or raw query results.
    Only sanitized, processed evidence is allowed here.
    """

    incident_id: UUID | None = None
    database_id: UUID | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)

    # Phase 3 — LLM context fields
    question: str = ""  # Natural language question from DBA
    intent: dict[str, Any] = Field(default_factory=dict)  # Parsed IntentResult
    hypotheses: list[Any] = Field(default_factory=list)  # list[Hypothesis]
    database_name: str = ""
    investigation_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sql_details: dict[str, Any] | None = None   # SQL text + plan summary (sanitized)
    source_fragment: str | None = None           # PL/SQL source fragment (±20 lines max)
    baseline_data: dict[str, Any] | None = None  # Historical baseline comparison

