import asyncio

from dependency_injector import containers, providers
from dependency_injector.providers import Callable, Factory, Singleton
from httpx import AsyncClient, Limits
from pybotx import Bot
from redis import asyncio as aioredis

from app.application.use_cases.record_use_cases import SampleRecordUseCases
from app.infrastructure.repositories.caching.callback_redis_repo import (
    CallbackRedisRepo,
)
from app.infrastructure.repositories.caching.exception_handlers import (
    PubsubExceptionHandler,
)
from app.infrastructure.repositories.caching.redis_repo import RedisRepo
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from app.logger import logger

from app.presentation.bot.error_handlers.internal_error_handler import (
    internal_error_handler,
)
from app.presentation.bot.middlewares.answer_error import answer_error_middleware
from app.presentation.bot.middlewares.smart_logger import smart_logger_middleware
from app.presentation.bot.resources import strings
from app.settings import settings


class BotSampleRecordCommandContainer(containers.DeclarativeContainer):
    record_use_cases_factory = Callable(
        lambda session: SampleRecordUseCases(
            record_repo=SampleRecordRepository(session=session)
        )
    )


# class StorageContainer(containers.DeclarativeContainer):
#     wiring_config = containers.WiringConfiguration(
#         modules=["app.presentation.bot.commands.sample_records"]
#     )
#
#     # Provider that returns a factory to create sessions
#     session_factory = Factory(build_db_session_factory)
#
#     # Provider that creates a session (e.g., AsyncSession instance)
#     session = Resource(session_factory)
#
#     # Provider that creates the SampleRecordUseCases, injecting the session
#     record_use_cases = Factory(
#         SampleRecordUseCases,
#         record_repo=Factory(
#             SampleRecordRepository,
#             session=session
#         )
#     )


class CallbackTaskManager:
    """Менеджер для управления задачей обработки callbacks"""

    def __init__(self, callback_repo: CallbackRedisRepo):
        self.callback_repo = callback_repo
        self._task: asyncio.Task | None = None

    def _get_task(self) -> asyncio.Task:
        """Получает или создает задачу в текущем цикле событий"""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(
                self.callback_repo.pubsub.run(
                    exception_handler=PubsubExceptionHandler()
                )
            )
        return self._task

    def _cancel_task(self) -> None:
        """Отменяет задачу если она существует"""
        if self._task and not self._task.done():
            self._task.cancel()

    async def shutdown(self) -> None:
        """Корректное завершение работы менеджера"""
        if self._task:
            self._cancel_task()
            try:
                await asyncio.gather(self._task, return_exceptions=True)
            except RuntimeError as e:
                logger.warning(f"Error at gather CallbackTaskManager tasks: {e}")

    def __call__(self) -> asyncio.Task:
        """Позволяет использовать как callable для провайдера"""
        return self._get_task()


class ApplicationStartupContainer(containers.DeclarativeContainer):
    """Container for application startup dependencies."""

    redis_client = Singleton(lambda: aioredis.from_url(settings.REDIS_DSN))

    redis_repo = Factory(
        RedisRepo,
        redis=redis_client,
        prefix=strings.BOT_PROJECT_NAME,
    )

    async_client = providers.Singleton(
        AsyncClient,
        timeout=settings.BOT_ASYNC_CLIENT_TIMEOUT_IN_SECONDS,
        limits=Limits(max_keepalive_connections=None, max_connections=None),
    )

    callback_repo = providers.Singleton(
        CallbackRedisRepo,
        redis=redis_client,
    )

    exception_handlers = (
        {} if not settings.RAISE_BOT_EXCEPTIONS else {Exception: internal_error_handler}
    )

    from app.presentation.bot.commands import common, sample_record

    bot = providers.Singleton(
        Bot,
        collectors=[common.collector, sample_record.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=settings.BOTX_CALLBACK_TIMEOUT_IN_SECONDS,
        httpx_client=async_client,
        middlewares=[
            smart_logger_middleware,
            answer_error_middleware,
        ],
        callback_repo=callback_repo,
    )

    # Используем менеджер задач для ленивой инициализации
    callback_task_manager = providers.Singleton(
        CallbackTaskManager,
        callback_repo,
    )

    # Провайдер который возвращает задачу через менеджер
    process_callbacks_task = providers.Callable(
        lambda manager: manager(),
        callback_task_manager,
    )


class WorkerStartupContainer(containers.DeclarativeContainer):
    redis_client = Singleton(lambda: aioredis.from_url(settings.REDIS_DSN))

    redis_repo = Factory(
        RedisRepo,
        redis=redis_client,
        prefix=strings.BOT_PROJECT_NAME,
    )

    async_client = providers.Singleton(
        AsyncClient,
        timeout=settings.BOT_ASYNC_CLIENT_TIMEOUT_IN_SECONDS,
        limits=Limits(max_keepalive_connections=None, max_connections=None),
    )

    callback_repo = providers.Singleton(
        CallbackRedisRepo,
        redis=redis_client,
    )
    from app.presentation.bot.commands import common, sample_record

    exception_handlers = (
        {} if not settings.RAISE_BOT_EXCEPTIONS else {Exception: internal_error_handler}
    )

    bot = providers.Singleton(
        Bot,
        collectors=[common.collector, sample_record.collector],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=settings.BOTX_CALLBACK_TIMEOUT_IN_SECONDS,
        httpx_client=async_client,
        middlewares=[
            smart_logger_middleware,
            answer_error_middleware,
        ],
        callback_repo=callback_repo,
    )
