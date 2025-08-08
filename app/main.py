"""Application with configuration for events, routers and middleware."""

from functools import partial

from dependency_injector.wiring import Provide
from fastapi import FastAPI
from pybotx import Bot

from app.infrastructure.containers import (
    ApplicationStartupContainer,
    BotSampleRecordCommandContainer,
)
from app.infrastructure.db.sqlalchemy import (
    get_engine,
    get_session_factory,
)
from app.presentation.api.routers import router
from app.presentation.bot.resources import strings


async def startup(
    bot: Bot,
) -> None:
    await bot.startup()


async def shutdown(
    container: ApplicationStartupContainer = Provide[ApplicationStartupContainer],
) -> None:
    await container.bot().shutdown()

    await container.callback_task_manager().shutdown()

    await container.redis_client().aclose()
    await get_engine().dispose()


def get_application() -> FastAPI:
    """Create configured server application instance."""

    # Initialize the main application container
    main_container = ApplicationStartupContainer()
    main_container.wire(
        modules=[
            "app.main",
            "app.presentation.api.botx",
            "app.presentation.bot.commands.sample_record",
        ]
    )

    # Initialize the SampleRecord commands container
    sample_record_commands_container = BotSampleRecordCommandContainer(
        session_factory=get_session_factory()
    )
    sample_record_commands_container.wire(
        modules=["app.presentation.bot.commands.sample_record"]
    )

    application = FastAPI(title=strings.BOT_PROJECT_NAME, openapi_url=None)

    # put bot to state only for tests
    application.state.bot = main_container.bot()

    application.add_event_handler(
        "startup",
        partial(startup, bot=main_container.bot()),
    )
    application.add_event_handler(
        "shutdown",
        partial(
            shutdown,
            # callback_task_manager=main_container.callback_task_manager(),
            # bot=main_container.bot(),
            # redis_client=main_container.redis_client(),
            container=main_container,
        ),
    )

    application.include_router(router)

    return application
