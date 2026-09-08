"""MCP tools — storage.py: 11 storage / health / scheduler tools + get_database_info."""

from __future__ import annotations

from oracle_mcp.oracle.repositories.sql_repo import SqlRepository
from oracle_mcp.oracle.repositories.storage_repo import StorageRepository
from oracle_mcp.security.audit import audit_context


# ── Database Info ─────────────────────────────────────────────────────────────

async def get_database_info() -> dict:
    """
    Return basic Oracle database and instance information.

    Sources: V$DATABASE, V$INSTANCE
    """
    args: dict = {}
    async with audit_context(tool="get_database_info", args=args):
        repo = SqlRepository()
        info = await repo.get_database_info()
        return info.model_dump(mode="json")


# ── Tablespace / Storage ──────────────────────────────────────────────────────

async def get_tablespace_usage() -> list[dict]:
    """
    Return storage usage for all tablespaces including used%, used bytes,
    free bytes, and total bytes.

    Sources: DBA_TABLESPACES, DBA_DATA_FILES, DBA_FREE_SPACE
    """
    args: dict = {}
    async with audit_context(tool="get_tablespace_usage", args=args):
        repo = StorageRepository()
        return await repo.get_tablespace_usage()


async def get_datafile_usage(tablespace_name: str) -> list[dict]:
    """
    Return individual datafile details for a specific tablespace.

    Sources: DBA_DATA_FILES
    """
    args = {"tablespace_name": tablespace_name.upper()}
    async with audit_context(tool="get_datafile_usage", args=args):
        repo = StorageRepository()
        return await repo.get_datafile_usage(tablespace_name.upper())


async def get_segment_growth(
    name: str,
    owner: str | None = None,
    segment_type: str | None = None,
) -> list[dict]:
    """
    Return current size information for a specific segment (table, index, LOB, etc.).

    Sources: DBA_SEGMENTS
    """
    args = {"name": name.upper(), "owner": owner, "segment_type": segment_type}
    async with audit_context(tool="get_segment_growth", args=args):
        repo = StorageRepository()
        return await repo.get_segment_growth(
            name=name.upper(), owner=owner, segment_type=segment_type
        )


async def get_temp_usage() -> list[dict]:
    """
    Return current TEMP tablespace usage (used%, total, free).

    Sources: DBA_TEMP_FILES, V$TEMPSTAT
    """
    args: dict = {}
    async with audit_context(tool="get_temp_usage", args=args):
        repo = StorageRepository()
        return await repo.get_temp_usage()


async def get_undo_usage() -> list[dict]:
    """
    Return recent UNDO tablespace statistics: active/unexpired/expired blocks,
    max query length, tuned retention.

    Sources: V$UNDOSTAT (last 12 periods = 1 hour)
    """
    args: dict = {}
    async with audit_context(tool="get_undo_usage", args=args):
        repo = StorageRepository()
        return await repo.get_undo_usage()


# ── Redo / Resource ───────────────────────────────────────────────────────────

async def get_redo_statistics(hours: int = 24) -> list[dict]:
    """
    Return online redo log status and archived log generation rate.

    Parameters
    ----------
    hours : int
        Look-back window for archived log rate (default 24).

    Sources: V$LOG, V$ARCHIVED_LOG
    """
    args = {"hours": hours}
    async with audit_context(tool="get_redo_statistics", args=args):
        repo = StorageRepository()
        logs = await repo.get_redo_statistics()
        archived = await repo.get_archived_log_rate(hours=hours)
        return {
            "online_logs": logs,
            "archived_log_rate_by_hour": archived,
        }


async def get_resource_usage() -> dict:
    """
    Return key system statistics: physical reads/writes, redo size,
    commits, rollbacks, parse counts, long table scans.

    Sources: V$SYSSTAT
    """
    args: dict = {}
    async with audit_context(tool="get_resource_usage", args=args):
        repo = StorageRepository()
        rows = await repo.get_resource_usage()
        # Convert to {name: value} dict for convenience
        return {row["name"]: row["value"] for row in rows}


# ── Scheduler Jobs ────────────────────────────────────────────────────────────

async def get_scheduler_jobs() -> list[dict]:
    """
    Return all Oracle Scheduler jobs with state, last run, next run,
    failure count, and run count.

    Sources: DBA_SCHEDULER_JOBS
    """
    args: dict = {}
    async with audit_context(tool="get_scheduler_jobs", args=args):
        repo = StorageRepository()
        return await repo.get_scheduler_jobs()


async def get_scheduler_job_history(
    job_name: str,
    owner: str | None = None,
    days: int = 7,
) -> list[dict]:
    """
    Return the execution history for a specific scheduler job.

    Parameters
    ----------
    job_name : str
        Scheduler job name.
    owner : str | None
        Schema owner of the job.
    days : int
        How many days of history to include (default 7).

    Sources: DBA_SCHEDULER_JOB_RUN_DETAILS
    """
    args = {"job_name": job_name.upper(), "owner": owner, "days": days}
    async with audit_context(tool="get_scheduler_job_history", args=args):
        repo = StorageRepository()
        return await repo.get_scheduler_job_history(
            job_name=job_name.upper(), owner=owner, days=days
        )


async def get_failed_jobs(hours: int = 24) -> list[dict]:
    """
    Return all scheduler jobs that failed (status != SUCCEEDED) in the last N hours.

    Parameters
    ----------
    hours : int
        Look-back window in hours (default 24).

    Sources: DBA_SCHEDULER_JOB_RUN_DETAILS
    """
    args = {"hours": hours}
    async with audit_context(tool="get_failed_jobs", args=args):
        repo = StorageRepository()
        return await repo.get_failed_jobs(hours=hours)
