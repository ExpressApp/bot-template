from dependency_injector import containers
from dependency_injector.providers import Factory, Callable, Singleton
from redis import asyncio as aioredis

from app.application.use_cases.record_use_cases import SampleRecordUseCases
from app.infrastructure.caching.redis_repo import RedisRepo
from app.infrastructure.repositories.sample_record import SampleRecordRepository
from app.infrastructure.db.sqlalchemy import build_db_session_factory
from app.presentation.bot.resources import strings
from app.settings import settings


class BotSampleRecordCommandContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.presentation.bot.commands.sample_records"]
    )

    # Session factory provider - returns a factory that creates AsyncSession instances
    session_factory = Factory(build_db_session_factory)

    record_use_cases_factory = Callable(
        lambda session: SampleRecordUseCases(
            record_repo=SampleRecordRepository(session=session)
        )
    )


class HealthCheckContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.presentation.api.healthcheck"]
    )

    # Session factory provider - returns a factory that creates AsyncSession instances
    session_factory = Factory(build_db_session_factory)

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


class ApplicationStartupContainer(containers.DeclarativeContainer):
    """Container for application startup dependencies."""

    wiring_config = containers.WiringConfiguration(modules=["app.main"])

    # Database
    # db_session_factory = Factory(build_db_session_factory)

    # Redis client
    redis_client = Singleton(
        aioredis.from_url,
        settings.REDIS_DSN,
    )

    redis_repo = Factory(
        RedisRepo,
        redis=redis_client,
        prefix=strings.BOT_PROJECT_NAME,
    )

    ## Configure connection pool for Redis
    # redis_connection_pool = Callable(
    #     lambda: aioredis.BlockingConnectionPool(
    #         max_connections=settings.REDIS_CONNECTION_POOL_SIZE,
    #         **(redis_client.provided.connection_pool.connection_kwargs),
    #     )
    # )
    #
    # # Set connection pool for Redis client
    # redis_client_with_pool = Callable(
    #     lambda: redis_client.provided.__setattr__(
    #         "connection_pool", redis_connection_pool()
    #     ) or redis_client.provided
    # )
    #
    # # Redis repo
    # redis_repo = Factory(
    #     RedisRepo,
    #     redis=redis_client_with_pool,
    #     prefix=strings.BOT_PROJECT_NAME,
    # )
    #
    # # Callback repo
    # callback_repo = Factory(
    #     CallbackRedisRepo,
    #     redis=redis_client_with_pool,
    # )
