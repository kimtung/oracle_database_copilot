from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db_copilot.api.routes.health import router as health_router
from db_copilot.api.routes.incidents import router as incidents_router
from db_copilot.api.routes.investigate import router as investigate_router
from db_copilot.api.routes.investigate_ws import router as investigate_ws_router
from db_copilot.api.routes.reports import router as reports_router
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

    # Enable CORS for frontend dashboard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(incidents_router, prefix=settings.api_v1_prefix)
    app.include_router(investigate_router, prefix=settings.api_v1_prefix)
    app.include_router(investigate_ws_router, prefix=settings.api_v1_prefix)
    app.include_router(reports_router, prefix=settings.api_v1_prefix)

    return app

