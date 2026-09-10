from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db_copilot.api.routes.health import router as health_router
from db_copilot.config.settings import get_settings
from db_copilot.db.session import close_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: resources can be initialized here
    yield
    # Shutdown: cleanup database engine pool
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

    return app
