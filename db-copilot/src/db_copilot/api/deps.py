from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db_copilot.db.session import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session
