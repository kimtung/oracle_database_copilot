import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db_copilot.db.schema import (
    Database,
    EvidenceItem,
    McpAuditLog,
    Snapshot,
    SqlBaseline,
    SqlMetric,
)
from db_copilot.domain.models.evidence import Evidence


class EvidenceRepository:
    """PostgreSQL repository for Evidence Engine entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_default_database(
        self,
        name: str = "PRIMARY_ORACLE",
        host: str = "localhost",
        service_name: str = "ORCL",
        version: str | None = "19c",
    ) -> Database:
        stmt = select(Database).where(Database.name == name)
        res = await self.session.execute(stmt)
        db_obj = res.scalar_one_or_none()
        if db_obj is None:
            db_obj = Database(
                name=name,
                host=host,
                service_name=service_name,
                version=version,
            )
            self.session.add(db_obj)
            await self.session.flush()
        return db_obj

    async def create_snapshot(
        self,
        database_id: uuid.UUID,
        captured_at: datetime | None = None,
        active_sessions: int | None = None,
        blocking_sessions: int | None = None,
        cpu_pct: float | None = None,
        health_score: int | None = None,
        raw_data: dict[str, Any] | None = None,
    ) -> Snapshot:
        snapshot = Snapshot(
            database_id=database_id,
            captured_at=captured_at or datetime.now(UTC),
            active_sessions=active_sessions,
            blocking_sessions=blocking_sessions,
            cpu_pct=cpu_pct,
            health_score=health_score,
            raw_data=raw_data,
        )
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def save_sql_metrics(
        self,
        metrics: list[dict[str, Any]],
        database_id: uuid.UUID,
        snapshot_id: uuid.UUID | None = None,
    ) -> list[SqlMetric]:
        created_metrics: list[SqlMetric] = []
        for m in metrics:
            captured_at = m.get("captured_at") or datetime.now(UTC)
            metric_obj = SqlMetric(
                database_id=database_id,
                snapshot_id=snapshot_id,
                sql_id=m["sql_id"],
                captured_at=captured_at,
                executions=m.get("executions"),
                elapsed_time_ms=m.get("elapsed_time_ms") or m.get("elapsed_time"),
                cpu_time_ms=m.get("cpu_time_ms") or m.get("cpu_time"),
                buffer_gets=m.get("buffer_gets"),
                disk_reads=m.get("disk_reads"),
                rows_processed=m.get("rows_processed"),
                plan_hash_value=m.get("plan_hash_value") or m.get("plan_hash"),
            )
            self.session.add(metric_obj)
            created_metrics.append(metric_obj)
        await self.session.flush()
        return created_metrics

    async def get_active_sql_ids(self, database_id: uuid.UUID, days: int = 7) -> list[str]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(SqlMetric.sql_id)
            .where(SqlMetric.database_id == database_id, SqlMetric.captured_at >= cutoff)
            .distinct()
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_sql_metrics_history(
        self, database_id: uuid.UUID, sql_id: str, days: int = 7
    ) -> list[SqlMetric]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(SqlMetric)
            .where(
                SqlMetric.database_id == database_id,
                SqlMetric.sql_id == sql_id,
                SqlMetric.captured_at >= cutoff,
            )
            .order_by(desc(SqlMetric.captured_at))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_sql_metrics_by_bucket(
        self,
        database_id: uuid.UUID,
        sql_id: str,
        hour_of_day: int,
        day_of_week: int,
        days: int = 7,
    ) -> list[SqlMetric]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        # Filter by time window and in-memory bucket to remain DB agnostic across SQLite / Postgres
        stmt = select(SqlMetric).where(
            SqlMetric.database_id == database_id,
            SqlMetric.sql_id == sql_id,
            SqlMetric.captured_at >= cutoff,
        )
        res = await self.session.execute(stmt)
        metrics = res.scalars().all()
        return [
            m for m in metrics
            if m.captured_at.hour == hour_of_day and m.captured_at.weekday() == day_of_week
        ]

    async def upsert_baseline(self, baseline: SqlBaseline) -> SqlBaseline:
        stmt = select(SqlBaseline).where(
            SqlBaseline.database_id == baseline.database_id,
            SqlBaseline.sql_id == baseline.sql_id,
            SqlBaseline.hour_of_day == baseline.hour_of_day,
            SqlBaseline.day_of_week == baseline.day_of_week,
        )
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.sample_count = baseline.sample_count
            existing.mean_elapsed_ms = baseline.mean_elapsed_ms
            existing.stddev_elapsed_ms = baseline.stddev_elapsed_ms
            existing.p50_elapsed_ms = baseline.p50_elapsed_ms
            existing.p95_elapsed_ms = baseline.p95_elapsed_ms
            existing.is_reliable = baseline.is_reliable
            existing.calculated_at = baseline.calculated_at or datetime.now(UTC)
            await self.session.flush()
            return existing

        self.session.add(baseline)
        await self.session.flush()
        return baseline

    async def get_baseline(
        self, database_id: uuid.UUID, sql_id: str, hour_of_day: int, day_of_week: int
    ) -> SqlBaseline | None:
        stmt = select(SqlBaseline).where(
            SqlBaseline.database_id == database_id,
            SqlBaseline.sql_id == sql_id,
            SqlBaseline.hour_of_day == hour_of_day,
            SqlBaseline.day_of_week == day_of_week,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_evidence(
        self, evidence: Evidence, incident_id: uuid.UUID | None = None
    ) -> EvidenceItem:
        item = EvidenceItem(
            id=evidence.id,
            incident_id=incident_id or evidence.incident_id,
            type=evidence.type.value if hasattr(evidence.type, "value") else str(evidence.type),
            source=evidence.source,
            timestamp=evidence.timestamp,
            entity_type=evidence.entity_type,
            entity_id=evidence.entity_id,
            severity=(
                evidence.severity.value
                if hasattr(evidence.severity, "value")
                else str(evidence.severity)
            ),
            data=evidence.data,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_evidence_by_incident(self, incident_id: uuid.UUID) -> list[EvidenceItem]:
        stmt = select(EvidenceItem).where(EvidenceItem.incident_id == incident_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def log_mcp_audit(
        self,
        tool_name: str,
        input_args: dict[str, Any] | None = None,
        duration_ms: int | None = None,
        rows_returned: int | None = None,
        status: str = "success",
        error_message: str | None = None,
        database_id: uuid.UUID | None = None,
    ) -> McpAuditLog:
        audit = McpAuditLog(
            database_id=database_id,
            tool_name=tool_name,
            input_args=input_args,
            duration_ms=duration_ms,
            rows_returned=rows_returned,
            status=status,
            error_message=error_message,
            occurred_at=datetime.now(UTC),
        )
        self.session.add(audit)
        await self.session.flush()
        return audit
