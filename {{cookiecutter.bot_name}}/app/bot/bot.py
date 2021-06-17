"""Configuration for bot instance."""
from botx import Bot, Depends
from botx_fsm import FSMMiddleware  # type: ignore
from botx_fsm.storages.redis import RedisStorage  # type: ignore
from loguru import logger

from app.bot.commands import common
from app.bot.dependencies.crud import auto_models_update
from app.bot.dependencies.errors import internal_error_handler
from app.bot.dependencies.external_cts import message_from_current_cts
from app.resources import strings
from app.settings.config import get_app_settings

config = get_app_settings()

redis_storage = RedisStorage(redis_dsn=str(config.REDIS_DSN), prefix=strings.BOT_NAME)
logger.debug(redis_storage.redis_dsn)
bot = Bot(
    bot_accounts=config.BOT_CREDENTIALS,
    dependencies=[Depends(message_from_current_cts), Depends(auto_models_update)],
)

bot.add_middleware(
    FSMMiddleware,
    storage=redis_storage,
    fsm_instances=[],
)

bot.startup_events = [redis_storage.init]
bot.shutdown_events = [redis_storage.close]

bot.include_collector(common.collector)

bot.add_exception_handler(Exception, internal_error_handler)
