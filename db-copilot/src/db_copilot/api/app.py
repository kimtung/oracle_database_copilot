from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db_copilot.api.routes.health import router as health_router
from db_copilot.api.routes.incidents import router as incidents_router
from db_copilot.config.settings import get_settings
from db_copilot.db.session import close_engine
from db_copilot.evidence.scheduler import EvidenceScheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    scheduler: EvidenceScheduler | None = None

    # Startup: Start evidence collection scheduler if enabled
    if settings.enable_scheduler:
        scheduler = EvidenceScheduler()
        scheduler.start()

    yield

    # Shutdown: Stop scheduler and cleanup database engine pool
    if scheduler is not None:
        scheduler.shutdown()

    await close_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Register API routers
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(incidents_router, prefix=settings.api_v1_prefix)

    return app
