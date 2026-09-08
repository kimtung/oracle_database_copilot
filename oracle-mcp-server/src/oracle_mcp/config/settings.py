"""Settings for oracle-mcp-server — all values come from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration loaded from environment variables or .env file.
    Oracle credentials MUST be provided via env — never hardcoded.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Oracle Connection ────────────────────────────────────────────────────
    oracle_user: str
    oracle_password: str
    oracle_dsn: str  # host:port/service_name  e.g. "db-host:1521/ORCL"

    # ── Connection Pool ──────────────────────────────────────────────────────
    oracle_pool_min: int = 2
    oracle_pool_max: int = 10
    oracle_pool_increment: int = 1
    oracle_query_timeout_sec: int = 30

    # ── MCP Transport ────────────────────────────────────────────────────────
    mcp_transport: str = "stdio"   # "stdio" | "sse"
    mcp_sse_port: int = 8080       # Only used when mcp_transport == "sse"

    # ── Audit ────────────────────────────────────────────────────────────────
    audit_log_enabled: bool = True


from functools import lru_cache


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.
    Loaded lazily — not at import time — so unit tests can patch env vars
    before the first call without requiring a real .env file.
    """
    return Settings()
