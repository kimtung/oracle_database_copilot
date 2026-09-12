import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_copilot.correlation.repository import IncidentRepository
from db_copilot.db.schema import Base, EvidenceItem
from db_copilot.domain.enums import EvidenceType, IncidentCategory, IncidentStatus, Severity
from db_copilot.domain.models.evidence import Evidence
from db_copilot.domain.models.incident import Incident


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_incident_with_evidence(async_session: AsyncSession):
    repo = IncidentRepository(async_session)

    ev1 = Evidence(
        type=EvidenceType.SQL_REGRESSION,
        source="V$SQLSTATS",
        entity_type="SQL",
        entity_id="sql_test_123",
        severity=Severity.HIGH,
        data={"multiplier": 4.5},
    )

    inc = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        title="SQL Regression on sql_test_123",
        description="Elapsed time increased 4.5x compared to baseline",
        evidence=[ev1],
    )

    created = await repo.create_incident(inc)
    assert created.id == inc.id
    assert created.title == inc.title
    assert len(created.evidence) == 1
    assert created.evidence[0].entity_id == "sql_test_123"

    # Fetch by ID
    detail = await repo.get_incident_by_id(created.id)
    assert detail is not None
    assert detail.incident.id == created.id
    assert len(detail.evidence) == 1
    assert detail.evidence[0].id == ev1.id


@pytest.mark.asyncio
async def test_list_incidents_with_filtering(async_session: AsyncSession):
    repo = IncidentRepository(async_session)

    inc1 = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.CRITICAL,
        title="Critical regression",
        status=IncidentStatus.OPEN,
    )
    inc2 = Incident(
        category=IncidentCategory.BLOCKING,
        severity=Severity.HIGH,
        title="Lock contention",
        status=IncidentStatus.OPEN,
    )
    inc3 = Incident(
        category=IncidentCategory.TABLESPACE,
        severity=Severity.MEDIUM,
        title="Tablespace warning",
        status=IncidentStatus.RESOLVED,
    )

    await repo.create_incident(inc1)
    await repo.create_incident(inc2)
    await repo.create_incident(inc3)

    # Filter by status
    open_incs = await repo.list_incidents(status=IncidentStatus.OPEN)
    assert len(open_incs) == 2

    # Filter by severity
    crit_incs = await repo.list_incidents(severity=Severity.CRITICAL)
    assert len(crit_incs) == 1
    assert crit_incs[0].title == "Critical regression"

    # Filter by category
    cap_incs = await repo.list_incidents(category=IncidentCategory.TABLESPACE)
    assert len(cap_incs) == 1
    assert cap_incs[0].title == "Tablespace warning"


@pytest.mark.asyncio
async def test_update_incident_status(async_session: AsyncSession):
    repo = IncidentRepository(async_session)

    inc = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        title="Performance issue",
        status=IncidentStatus.OPEN,
    )
    created = await repo.create_incident(inc)

    # Transition to INVESTIGATING
    inv = await repo.update_incident_status(created.id, IncidentStatus.INVESTIGATING)
    assert inv is not None
    assert inv.status == IncidentStatus.INVESTIGATING
    assert inv.resolved_at is None

    # Transition to RESOLVED
    resolved = await repo.update_incident_status(created.id, IncidentStatus.RESOLVED)
    assert resolved is not None
    assert resolved.status == IncidentStatus.RESOLVED
    assert resolved.resolved_at is not None


@pytest.mark.asyncio
async def test_attach_evidence_to_incident(async_session: AsyncSession):
    repo = IncidentRepository(async_session)

    # Standalone evidence item
    ev_item = EvidenceItem(
        id=uuid.uuid4(),
        type=EvidenceType.BLOCKING_SESSION.value,
        source="V$SESSION",
        entity_type="SESSION",
        entity_id="123",
        severity="MEDIUM",
    )
    async_session.add(ev_item)
    await async_session.flush()

    # Create incident
    inc = Incident(
        category=IncidentCategory.BLOCKING,
        severity=Severity.MEDIUM,
        title="Blocking detected",
    )
    created = await repo.create_incident(inc)

    # Attach evidence
    success = await repo.attach_evidence_to_incident(created.id, ev_item.id)
    assert success is True

    # Check incident detail
    detail = await repo.get_incident_by_id(created.id)
    assert detail is not None
    assert len(detail.evidence) == 1
    assert detail.evidence[0].id == ev_item.id


@pytest.mark.asyncio
async def test_find_open_incident_deduplication(async_session: AsyncSession):
    repo = IncidentRepository(async_session)

    ev = Evidence(
        type=EvidenceType.SQL_REGRESSION,
        source="V$SQL",
        entity_type="SQL",
        entity_id="sql_dup_check",
    )
    inc = Incident(
        category=IncidentCategory.SQL_REGRESSION,
        severity=Severity.HIGH,
        title="SQL Regression sql_dup_check",
        description="Regression detected for sql_dup_check",
        evidence=[ev],
        status=IncidentStatus.OPEN,
    )
    await repo.create_incident(inc)

    # Search for matching open incident
    found = await repo.find_open_incident(
        IncidentCategory.SQL_REGRESSION, "sql_dup_check", within_minutes=60
    )
    assert found is not None
    assert found.id == inc.id

    # If incident is resolved, it should not be returned by deduplication
    await repo.update_incident_status(inc.id, IncidentStatus.RESOLVED)
    found_after_resolve = await repo.find_open_incident(
        IncidentCategory.SQL_REGRESSION, "sql_dup_check", within_minutes=60
    )
    assert found_after_resolve is None
