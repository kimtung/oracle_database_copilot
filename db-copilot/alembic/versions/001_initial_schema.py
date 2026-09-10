"""001_initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-10 14:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # databases
    op.create_table(
        "databases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("host", sa.String(length=256), nullable=False),
        sa.Column("service_name", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # snapshots
    op.create_table(
        "snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("active_sessions", sa.Integer(), nullable=True),
        sa.Column("blocking_sessions", sa.Integer(), nullable=True),
        sa.Column("cpu_pct", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("health_score", sa.Integer(), nullable=True),
        sa.Column(
            "raw_data",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_snapshots_db_time",
        "snapshots",
        ["database_id", sa.text("captured_at DESC")],
    )

    # sql_metrics
    op.create_table(
        "sql_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=True),
        sa.Column("sql_id", sa.String(length=13), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("executions", sa.BigInteger(), nullable=True),
        sa.Column("elapsed_time_ms", sa.BigInteger(), nullable=True),
        sa.Column("cpu_time_ms", sa.BigInteger(), nullable=True),
        sa.Column("buffer_gets", sa.BigInteger(), nullable=True),
        sa.Column("disk_reads", sa.BigInteger(), nullable=True),
        sa.Column("rows_processed", sa.BigInteger(), nullable=True),
        sa.Column("plan_hash_value", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_sql_metrics_id_time",
        "sql_metrics",
        ["database_id", "sql_id", sa.text("captured_at DESC")],
    )

    # sql_baselines
    op.create_table(
        "sql_baselines",
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("sql_id", sa.String(length=13), nullable=False),
        sa.Column("hour_of_day", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=True),
        sa.Column("mean_elapsed_ms", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("stddev_elapsed_ms", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("p50_elapsed_ms", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("p95_elapsed_ms", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("is_reliable", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("database_id", "sql_id", "hour_of_day", "day_of_week"),
    )

    # incidents
    op.create_table(
        "incidents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column(
            "diagnosis",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_incidents_db_sev",
        "incidents",
        ["database_id", "severity", sa.text("detected_at DESC")],
    )

    # evidence_items
    op.create_table(
        "evidence_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("incident_id", sa.Uuid(), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=True),
        sa.Column("source", sa.String(length=128), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("entity_type", sa.String(length=32), nullable=True),
        sa.Column("entity_id", sa.String(length=128), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column(
            "data",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # mcp_audit_log
    op.create_table(
        "mcp_audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("database_id", sa.Uuid(), nullable=True),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column(
            "input_args",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("rows_returned", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_time", "mcp_audit_log", [sa.text("occurred_at DESC")])

    # daily_reports
    op.create_table(
        "daily_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=True),
        sa.Column("content_markdown", sa.Text(), nullable=True),
        sa.Column(
            "content_json",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["database_id"], ["databases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("database_id", "report_date", name="uq_daily_reports_db_date"),
    )


def downgrade() -> None:
    op.drop_table("daily_reports")
    op.drop_index("idx_audit_time", table_name="mcp_audit_log")
    op.drop_table("mcp_audit_log")
    op.drop_table("evidence_items")
    op.drop_index("idx_incidents_db_sev", table_name="incidents")
    op.drop_table("incidents")
    op.drop_table("sql_baselines")
    op.drop_index("idx_sql_metrics_id_time", table_name="sql_metrics")
    op.drop_table("sql_metrics")
    op.drop_index("idx_snapshots_db_time", table_name="snapshots")
    op.drop_table("snapshots")
    op.drop_table("databases")
