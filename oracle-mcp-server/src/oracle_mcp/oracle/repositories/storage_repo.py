"""Repository for storage, jobs, redo, and database health."""

from __future__ import annotations

from oracle_mcp.oracle.queries import storage_queries as Q
from oracle_mcp.oracle.repositories.base import BaseRepository


class StorageRepository(BaseRepository):

    # ── Tablespace / Storage ──────────────────────────────────────────────

    async def get_tablespace_usage(self) -> list[dict]:
        return await self._fetchall(Q.TABLESPACE_USAGE)

    async def get_datafile_usage(self, tablespace_name: str) -> list[dict]:
        return await self._fetchall(Q.DATAFILE_USAGE, {"tablespace_name": tablespace_name})

    async def get_temp_usage(self) -> list[dict]:
        return await self._fetchall(Q.TEMP_USAGE)

    async def get_undo_usage(self) -> list[dict]:
        return await self._fetchall(Q.UNDO_USAGE)

    async def get_segment_growth(
        self,
        name: str,
        owner: str | None = None,
        segment_type: str | None = None,
    ) -> list[dict]:
        return await self._fetchall(
            Q.SEGMENT_GROWTH,
            {"name": name, "owner": owner, "segment_type": segment_type},
        )

    # ── Redo / Alert ──────────────────────────────────────────────────────

    async def get_redo_statistics(self) -> list[dict]:
        return await self._fetchall(Q.REDO_STATISTICS)

    async def get_archived_log_rate(self, hours: int = 24) -> list[dict]:
        return await self._fetchall(Q.ARCHIVED_LOG_RATE, {"hours": hours})

    async def get_resource_usage(self) -> list[dict]:
        return await self._fetchall(Q.RESOURCE_USAGE)

    # ── Scheduler Jobs ────────────────────────────────────────────────────

    async def get_scheduler_jobs(self) -> list[dict]:
        return await self._fetchall(Q.SCHEDULER_JOBS)

    async def get_scheduler_job_history(
        self, job_name: str, owner: str | None = None, days: int = 7
    ) -> list[dict]:
        return await self._fetchall(
            Q.SCHEDULER_JOB_HISTORY,
            {"job_name": job_name, "owner": owner, "days": days},
        )

    async def get_failed_jobs(self, hours: int = 24) -> list[dict]:
        return await self._fetchall(Q.FAILED_JOBS, {"hours": hours})
