"""Application with configuration for events, routers and middleware."""
from botx import UnknownBotError
from fastapi import FastAPI

from app.api.error_handlers import unknown_bot
from app.api.routers import router
from app.bot.bot import bot
from app.settings.config import get_app_settings
from app.settings.events import shutdown, startup

config = get_app_settings()


def get_application() -> FastAPI:
    """Create configured server application instance."""
    application = FastAPI(title="{{cookiecutter.bot_name}}")
    application.state = bot.state
    application.state.bot = bot

    application.add_event_handler(
        "startup",
        startup(
            redis_dsn=config.REDIS_DSN,
            redis_prefix="{{cookiecutter.bot_name}}",
            bot_app=bot,
        ),
    )

    application.add_event_handler("shutdown", shutdown(bot_app=bot))

    application.add_exception_handler(
        UnknownBotError, unknown_bot.message_from_unknown_bot_handler
    )

    application.include_router(router)

    return application


app = get_application()
