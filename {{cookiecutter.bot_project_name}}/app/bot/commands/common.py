"""Handlers for default bot commands and system events."""

from os import environ

from pybotx import (
    Bot,
    BotShuttingDownError,
    BubbleMarkup,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    StatusRecipient,
)

from app.bot.middlewares.db_session import db_session_middleware
from app.db.record.repo import RecordRepo
from app.resources import strings

collector = HandlerCollector()


@collector.command("/_test-fail-shutting-down", visible=False)
async def test_fail_shutting_down(message: IncomingMessage, bot: Bot) -> None:
    """Testing fail while shutting down."""
    raise BotShuttingDownError("test")


@collector.command("/_test-fail", visible=False)
async def test_fail(message: IncomingMessage, bot: Bot) -> None:
    """Testing internal error."""
    raise ValueError


@collector.command("/_test-redis", visible=False)
async def test_redis(message: IncomingMessage, bot: Bot) -> None:
    """Testing redis."""
    # This test just for coverage
    # Better to assert bot answers instead of using direct DB/Redis access

    redis_repo = bot.state.redis_repo

    await redis_repo.set("test_key", "test_value")


@collector.command("/_test-db", visible=False, middlewares=[db_session_middleware])
async def test_db(message: IncomingMessage, bot: Bot) -> None:
    """Testing db session."""
    # This test just for coverage
    # Better to assert bot answers instead of using direct DB/Redis access

    # add text to history
    # example of using database
    record_repo = RecordRepo(message.state.db_session)

    await record_repo.create(record_data="test 1")
    await record_repo.update(record_id=1, record_data="test 1 (updated)")

    await record_repo.create(record_data="test 2")
    await record_repo.delete(record_id=2)

    await record_repo.create(record_data="test not unique data")
    await record_repo.create(record_data="test not unique data")


@collector.default_message_handler
async def default_handler(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    """Run if command handler not found."""

    await bot.answer_message("Hello!")


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    """Send a welcome message and the bot functionality in new created chat."""

    answer_body = strings.CHAT_CREATED_TEMPLATE.format(
        bot_project_name=strings.BOT_DISPLAY_NAME
    )
    bubbles = BubbleMarkup()
    bubbles.add_button(command="/help", label=strings.HELP_LABEL)

    await bot.answer_message(answer_body, bubbles=bubbles)


@collector.command("/help", description="Get available commands")
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    """Show commands list."""

    status_recipient = StatusRecipient.from_incoming_message(message)

    status = await bot.get_status(status_recipient)
    command_map = dict(sorted(status.items()))

    answer_body = "\n".join(
        f"`{command}` -- {description}" for command, description in command_map.items()
    )

    await bot.answer_message(answer_body)


@collector.command("/_debug:git-commit-sha", visible=False)
async def git_commit_sha(message: IncomingMessage, bot: Bot) -> None:
    """Show git commit SHA."""

    await bot.answer_message(environ.get("GIT_COMMIT_SHA", "<undefined>"))
