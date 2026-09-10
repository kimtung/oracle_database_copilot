import uuid
from datetime import UTC, date, datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid


class Base(DeclarativeBase):
    pass


class Database(Base):
    __tablename__ = "databases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(256), nullable=False)
    service_name: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    snapshots: Mapped[list["Snapshot"]] = relationship("Snapshot", back_populates="database")
    incidents: Mapped[list["Incident"]] = relationship("Incident", back_populates="database")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    database_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="CASCADE"), nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_sessions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    blocking_sessions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cpu_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    database: Mapped["Database"] = relationship("Database", back_populates="snapshots")
    sql_metrics: Mapped[list["SqlMetric"]] = relationship("SqlMetric", back_populates="snapshot")

    __table_args__ = (
        Index("idx_snapshots_db_time", "database_id", captured_at.desc()),
    )


class SqlMetric(Base):
    __tablename__ = "sql_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    database_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("snapshots.id", ondelete="SET NULL"), nullable=True
    )
    sql_id: Mapped[str] = mapped_column(String(13), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    executions: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    elapsed_time_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    cpu_time_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    buffer_gets: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    disk_reads: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    rows_processed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    plan_hash_value: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    snapshot: Mapped[Optional["Snapshot"]] = relationship("Snapshot", back_populates="sql_metrics")

    __table_args__ = (
        Index("idx_sql_metrics_id_time", "database_id", "sql_id", captured_at.desc()),
    )


class SqlBaseline(Base):
    __tablename__ = "sql_baselines"

    database_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="CASCADE"), primary_key=True
    )
    sql_id: Mapped[str] = mapped_column(String(13), primary_key=True)
    hour_of_day: Mapped[int] = mapped_column(Integer, primary_key=True)  # 0-23
    day_of_week: Mapped[int] = mapped_column(Integer, primary_key=True)  # 0-6 (Mon-Sun)
    sample_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mean_elapsed_ms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    stddev_elapsed_ms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    p50_elapsed_ms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    p95_elapsed_ms: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    is_reliable: Mapped[bool] = mapped_column(Boolean, default=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    database_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="CASCADE"), nullable=True
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="OPEN")
    diagnosis: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    database: Mapped[Optional["Database"]] = relationship("Database", back_populates="incidents")
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem", back_populates="incident"
    )

    __table_args__ = (
        Index("idx_incidents_db_sev", "database_id", "severity", detected_at.desc()),
    )


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    incident: Mapped["Incident | None"] = relationship(
        "Incident", back_populates="evidence_items"
    )


class McpAuditLog(Base):
    __tablename__ = "mcp_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    database_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="SET NULL"), nullable=True
    )
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    input_args: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rows_returned: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_audit_time", occurred_at.desc()),
    )


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    database_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("databases.id", ondelete="CASCADE"), nullable=True
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("database_id", "report_date", name="uq_daily_reports_db_date"),
    )
