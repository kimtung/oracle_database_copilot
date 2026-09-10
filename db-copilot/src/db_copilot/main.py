import uvicorn

from db_copilot.api.app import create_app
from db_copilot.config.settings import get_settings

app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "db_copilot.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
