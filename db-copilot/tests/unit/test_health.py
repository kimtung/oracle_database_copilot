from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from db_copilot.domain.enums import EvidenceType, IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models import DiagnosisResult, Evidence, Incident, Recommendation


@pytest.mark.asyncio
async def test_health_check_returns_200_when_database_connected(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_returns_503_when_database_disconnected(
    client: AsyncClient, mock_db_session: AsyncMock
):
    mock_db_session.execute.side_effect = Exception("DB connection timeout")

    response = await client.get("/api/v1/health")
    assert response.status_code == 503

    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"] == "disconnected"
    assert data["version"] == "0.1.0"


def test_domain_models_creation():
    ev = Evidence(
        type=EvidenceType.SQL_REGRESSION,
        source="V$SQL",
        entity_type="SQL",
        entity_id="8f3abc12345",
        severity=Severity.HIGH,
        data={"elapsed_time_ms": 12000},
    )
    assert ev.type == EvidenceType.SQL_REGRESSION
    assert ev.severity == Severity.HIGH
    assert ev.entity_id == "8f3abc12345"

    inc = Incident(
        title="High elapsed time on SQL 8f3abc12345",
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        evidence=[ev],
    )
    assert inc.category == IncidentCategory.SQL_REGRESSION
    assert inc.status == IncidentStatus.OPEN
    assert len(inc.evidence) == 1

    rec = Recommendation(
        action="Gather table and index statistics",
        rationale="Stale stats causing bad execution plan",
        sql="EXEC DBMS_STATS.GATHER_TABLE_STATS('APP', 'ORDERS');",
    )
    diag = DiagnosisResult(
        diagnosis="Execution plan changed due to stale statistics",
        confidence=0.85,
        primary_cause="Stale statistics on ORDERS table",
        evidence_used=["Plan changed from index scan to full table scan"],
        recommendations=[rec],
    )
    assert diag.confidence == 0.85
    assert len(diag.recommendations) == 1
    assert diag.recommendations[0].risk == "LOW"
