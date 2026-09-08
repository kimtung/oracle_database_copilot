"""Unit tests for oracle-mcp-server Phase 0.

All tests mock the Oracle repository so no real Oracle instance is needed.
Run with: pytest tests/unit/ -v
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from oracle_mcp.models.response_models import (
    BlockedSession,
    BlockingChain,
    BlockingResult,
    DatabaseInfo,
    LongRunningSession,
    Session,
    SqlStatistics,
    SqlSummary,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db_info():
    return DatabaseInfo(
        db_name="ORCL",
        db_unique_name="ORCL",
        instance_name="ORCL1",
        host_name="db-server-01",
        version="19.3.0.0.0",
        status="OPEN",
        log_mode="ARCHIVELOG",
        logins="ALLOWED",
        startup_time=datetime(2026, 9, 1, 8, 0, 0),
    )


@pytest.fixture
def mock_sql_summary():
    return SqlSummary(
        sql_id="8f3abcde12345",
        sql_text_fragment="SELECT * FROM ACCOUNT_POSITION WHERE STATUS = :1",
        executions=12450,
        elapsed_time_sec=52300.0,
        cpu_time_sec=21300.0,
        buffer_gets=182000000,
        disk_reads=9300000,
        rows_processed=4200000,
        plan_hash_value=98237412,
        module="PROC_SETTLEMENT",
        action="UPDATE_PHASE",
        last_active_time=datetime(2026, 9, 8, 14, 32, 0),
    )


@pytest.fixture
def mock_blocking_result():
    chain = BlockingChain(
        blocker_sid=142,
        blocker_serial=1023,
        blocker_user="APP",
        blocker_sql_id="abc123",
        blocker_wait_event="enq: TX - row lock contention",
        blocker_elapsed_sec=423,
        blocked_sessions=[
            BlockedSession(
                blocked_sid=156,
                blocked_serial=2011,
                blocked_user="APP",
                blocked_sql_id="def456",
                blocked_wait_event="enq: TX - row lock contention",
                blocked_wait_sec=423,
            )
        ],
    )
    return BlockingResult(
        blocking_chains=[chain],
        total_blocked=1,
        max_wait_seconds=423,
    )


# ── get_database_info ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_database_info_returns_correct_schema(mock_db_info):
    with patch(
        "oracle_mcp.tools.storage.SqlRepository.get_database_info",
        new_callable=AsyncMock,
        return_value=mock_db_info,
    ):
        from oracle_mcp.tools.storage import get_database_info

        result = await get_database_info()

    assert result["db_name"] == "ORCL"
    assert result["version"] == "19.3.0.0.0"
    assert result["instance_name"] == "ORCL1"
    assert result["host_name"] == "db-server-01"
    assert result["status"] == "OPEN"


@pytest.mark.asyncio
async def test_get_database_info_writes_audit_log(mock_db_info, capsys):
    with patch(
        "oracle_mcp.tools.storage.SqlRepository.get_database_info",
        new_callable=AsyncMock,
        return_value=mock_db_info,
    ):
        from oracle_mcp.tools.storage import get_database_info

        await get_database_info()

    captured = capsys.readouterr()
    audit = json.loads(captured.err.strip().splitlines()[-1])

    assert audit["tool"] == "get_database_info"
    assert audit["status"] == "success"
    assert "duration_ms" in audit


# ── get_top_sql ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_top_sql_returns_list(mock_sql_summary):
    with patch(
        "oracle_mcp.tools.sql.SqlRepository.get_top_sql",
        new_callable=AsyncMock,
        return_value=[mock_sql_summary],
    ):
        from oracle_mcp.tools.sql import get_top_sql

        result = await get_top_sql(metric="elapsed_time", limit=10, hours=1)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["sql_id"] == "8f3abcde12345"
    assert result[0]["module"] == "PROC_SETTLEMENT"
    assert result[0]["executions"] == 12450


@pytest.mark.asyncio
async def test_get_top_sql_invalid_metric_raises():
    from oracle_mcp.tools.sql import get_top_sql

    with pytest.raises(ValueError, match="Invalid metric"):
        await get_top_sql(metric="invalid_metric")


@pytest.mark.asyncio
async def test_get_top_sql_limit_capped_at_100(mock_sql_summary):
    """limit > 100 must be silently capped to 100."""
    with patch(
        "oracle_mcp.tools.sql.SqlRepository.get_top_sql",
        new_callable=AsyncMock,
        return_value=[mock_sql_summary],
    ) as mock_repo:
        from oracle_mcp.tools.sql import get_top_sql

        await get_top_sql(metric="cpu", limit=999)

    # The repo must be called with limit=100 (capped)
    call_kwargs = mock_repo.call_args.kwargs
    assert call_kwargs["limit"] == 100


# ── get_sql_statistics ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_sql_statistics_returns_correct_schema():
    stats = SqlStatistics(
        sql_id="8f3abcde12345",
        sql_text="SELECT * FROM ACCOUNT_POSITION WHERE STATUS = :1",
        executions=12450,
        elapsed_time_sec=52300.0,
        cpu_time_sec=21300.0,
        buffer_gets=182000000,
        disk_reads=9300000,
        rows_processed=4200000,
        plan_hash_value=98237412,
        module="PROC_SETTLEMENT",
        avg_elapsed_sec=4.2,
        avg_disk_reads=747.0,
    )
    with patch(
        "oracle_mcp.tools.sql.SqlRepository.get_sql_statistics",
        new_callable=AsyncMock,
        return_value=stats,
    ):
        from oracle_mcp.tools.sql import get_sql_statistics

        result = await get_sql_statistics("8f3abcde12345")

    assert result is not None
    assert result["sql_id"] == "8f3abcde12345"
    assert result["avg_elapsed_sec"] == 4.2
    assert result["module"] == "PROC_SETTLEMENT"


@pytest.mark.asyncio
async def test_get_sql_statistics_returns_none_when_not_found():
    with patch(
        "oracle_mcp.tools.sql.SqlRepository.get_sql_statistics",
        new_callable=AsyncMock,
        return_value=None,
    ):
        from oracle_mcp.tools.sql import get_sql_statistics

        result = await get_sql_statistics("nonexistent")

    assert result is None


# ── get_active_sessions ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_active_sessions_returns_list():
    session = Session(
        sid=142,
        serial=1023,
        username="APP",
        status="ACTIVE",
        sql_id="abc123",
        module="PROC_SETTLEMENT",
        elapsed_seconds=423,
        wait_event="db file sequential read",
    )
    with patch(
        "oracle_mcp.tools.session.SqlRepository.get_active_sessions",
        new_callable=AsyncMock,
        return_value=[session],
    ):
        from oracle_mcp.tools.session import get_active_sessions

        result = await get_active_sessions(min_elapsed_sec=0)

    assert isinstance(result, list)
    assert result[0]["sid"] == 142
    assert result[0]["username"] == "APP"
    assert result[0]["elapsed_seconds"] == 423


# ── get_blocking_sessions ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_blocking_sessions_returns_chain(mock_blocking_result):
    with patch(
        "oracle_mcp.tools.session.SqlRepository.get_blocking_sessions",
        new_callable=AsyncMock,
        return_value=mock_blocking_result,
    ):
        from oracle_mcp.tools.session import get_blocking_sessions

        result = await get_blocking_sessions()

    assert result["total_blocked"] == 1
    assert result["max_wait_seconds"] == 423
    assert len(result["blocking_chains"]) == 1
    chain = result["blocking_chains"][0]
    assert chain["blocker_sid"] == 142
    assert len(chain["blocked_sessions"]) == 1


@pytest.mark.asyncio
async def test_get_blocking_sessions_returns_empty_when_none():
    empty = BlockingResult(blocking_chains=[], total_blocked=0, max_wait_seconds=0)
    with patch(
        "oracle_mcp.tools.session.SqlRepository.get_blocking_sessions",
        new_callable=AsyncMock,
        return_value=empty,
    ):
        from oracle_mcp.tools.session import get_blocking_sessions

        result = await get_blocking_sessions()

    assert result["total_blocked"] == 0
    assert result["blocking_chains"] == []


# ── Audit log always written ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_log_written_on_error(capsys):
    with patch(
        "oracle_mcp.tools.session.SqlRepository.get_blocking_sessions",
        new_callable=AsyncMock,
        side_effect=Exception("ORA-00942: table or view does not exist"),
    ):
        from oracle_mcp.tools.session import get_blocking_sessions

        with pytest.raises(Exception, match="ORA-00942"):
            await get_blocking_sessions()

    captured = capsys.readouterr()
    audit = json.loads(captured.err.strip().splitlines()[-1])

    assert audit["tool"] == "get_blocking_sessions"
    assert audit["status"] == "error"
    assert "ORA-00942" in audit["error"]


# ── Security: no credentials in audit log ────────────────────────────────────

def test_sanitizer_removes_password():
    from oracle_mcp.security.sanitizer import sanitize_args

    raw = {
        "sql_id": "abc123",
        "password": "SUPER_SECRET",
        "oracle_user": "db_copilot",
    }
    result = sanitize_args(raw)

    assert result["sql_id"] == "abc123"
    assert result["password"] == "***"
    assert result["oracle_user"] == "***"


def test_sanitizer_preserves_safe_fields():
    from oracle_mcp.security.sanitizer import sanitize_args

    raw = {"metric": "elapsed_time", "limit": 20, "hours": 1}
    result = sanitize_args(raw)

    assert result == raw


def test_sanitizer_masks_nested_credentials():
    from oracle_mcp.security.sanitizer import sanitize_args

    raw = {"connection": {"user": "app", "password": "secret"}}
    result = sanitize_args(raw)

    assert result["connection"]["password"] == "***"
    assert result["connection"]["user"] == "app"
