import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.api.app import create_app
from db_copilot.api.deps import get_db_session
from db_copilot.correlation.repository import IncidentRepository
from db_copilot.db.schema import Base
from db_copilot.domain.enums import EvidenceType, IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import Incident


@pytest.fixture
async def app_client() -> AsyncGenerator[tuple[AsyncClient, IncidentRepository], None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    app = create_app()

    async with session_maker() as session:
        repo = IncidentRepository(session)

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db_session] = override_get_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac, repo

        app.dependency_overrides.clear()

    await engine.dispose()


@pytest.mark.asyncio
async def test_api_list_incidents(app_client):
    client, repo = app_client

    inc1 = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        title="SQL Regression",
        status=IncidentStatus.OPEN,
    )
    inc2 = Incident(
        category=IncidentCategory.BLOCKING,
        severity=Severity.CRITICAL,
        title="Lock contention",
        status=IncidentStatus.RESOLVED,
    )
    await repo.create_incident(inc1)
    await repo.create_incident(inc2)

    # List all
    res = await client.get("/api/v1/incidents")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

    # Filter by status
    res_open = await client.get("/api/v1/incidents?status=OPEN")
    assert res_open.status_code == 200
    assert len(res_open.json()) == 1
    assert res_open.json()[0]["title"] == "SQL Regression"

    # Filter by category
    res_cat = await client.get("/api/v1/incidents?category=BLOCKING")
    assert res_cat.status_code == 200
    assert len(res_cat.json()) == 1
    assert res_cat.json()[0]["title"] == "Lock contention"


@pytest.mark.asyncio
async def test_api_get_incident_detail_and_404(app_client):
    client, repo = app_client

    ev = Evidence(
        type=EvidenceType.SQL_REGRESSION,
        source="V$SQLSTATS",
        entity_type="SQL",
        entity_id="sql_api_test",
        severity=Severity.HIGH,
    )
    inc = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        title="API Test Regression",
        evidence=[ev],
    )
    created = await repo.create_incident(inc)

    # Get by ID
    res = await client.get(f"/api/v1/incidents/{created.id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["incident"]["id"] == str(created.id)
    assert len(detail["evidence"]) == 1
    assert detail["evidence"][0]["entity_id"] == "sql_api_test"

    # 404 for non-existent incident
    fake_id = uuid.uuid4()
    res_404 = await client.get(f"/api/v1/incidents/{fake_id}")
    assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_api_resolve_incident(app_client):
    client, repo = app_client

    inc = Incident(
        category=IncidentCategory.TABLESPACE,
        severity=Severity.CRITICAL,
        title="Tablespace full",
        status=IncidentStatus.OPEN,
    )
    created = await repo.create_incident(inc)

    # Resolve incident
    res = await client.patch(f"/api/v1/incidents/{created.id}/resolve")
    assert res.status_code == 200
    resolved = res.json()
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_at"] is not None
