from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "DB Copilot"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"

    # PostgreSQL Database
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "db_copilot"
    postgres_url: str | None = None

    # MCP Server Gateway
    mcp_server_command: str = "python"
    mcp_server_args: list[str] = ["-m", "oracle_mcp.server"]
    mcp_server_cwd: str | None = None
    oracle_user: str = "db_copilot_readonly"
    oracle_password: str = ""
    oracle_dsn: str = "localhost:1521/ORCL"

    # Evidence Engine & Scheduler
    enable_scheduler: bool = True
    collection_interval_minutes: int = 5
    baseline_recalc_interval_hours: int = 1
    sql_regression_multiplier: float = 3.0
    tablespace_warning_threshold: float = 80.0
    tablespace_critical_threshold: float = 90.0
    long_running_threshold_sec: int = 1800

    @property
    def database_url(self) -> str:
        if self.postgres_url:
            return self.postgres_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
