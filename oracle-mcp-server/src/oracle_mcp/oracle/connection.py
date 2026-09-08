"""Oracle async connection pool — python-oracledb thin mode."""

from __future__ import annotations

import logging

import oracledb

from oracle_mcp.config.settings import get_settings

logger = logging.getLogger(__name__)

# ── Pool singleton ──────────────────────────────────────────────────────────

_pool: oracledb.AsyncConnectionPool | None = None


async def get_pool() -> oracledb.AsyncConnectionPool:
    """
    Return the singleton async connection pool, creating it on first call.
    python-oracledb thin mode — no Oracle Instant Client required.
    """
    global _pool

    if _pool is None:
        s = get_settings()
        logger.info(
            "Initialising Oracle connection pool: dsn=%s user=%s min=%d max=%d",
            s.oracle_dsn,
            s.oracle_user,
            s.oracle_pool_min,
            s.oracle_pool_max,
        )
        _pool = await oracledb.create_pool_async(
            user=s.oracle_user,
            password=s.oracle_password,
            dsn=s.oracle_dsn,
            min=s.oracle_pool_min,
            max=s.oracle_pool_max,
            increment=s.oracle_pool_increment,
        )
        logger.info("Oracle connection pool ready.")

    return _pool


async def close_pool() -> None:
    """Gracefully close the pool (call on shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Oracle connection pool closed.")
