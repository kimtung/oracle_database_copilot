from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db_copilot.api.deps import get_db_session
from db_copilot.config.settings import get_settings
from db_copilot.db.session import check_db_connection

router = APIRouter(tags=["Health"])


class HealthStatus(BaseModel):
    status: str
    database: str
    version: str
    timestamp: datetime


@router.get("/health", response_model=HealthStatus)
async def get_health(
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> HealthStatus:
    settings = get_settings()
    is_db_connected = await check_db_connection(db)

    if is_db_connected:
        health_status = "healthy"
        db_status = "connected"
    else:
        health_status = "degraded"
        db_status = "disconnected"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthStatus(
        status=health_status,
        database=db_status,
        version=settings.app_version,
        timestamp=datetime.now(UTC),
    )
