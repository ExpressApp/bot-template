"""Handlers for default bot commands and system events."""

from os import environ

from pybotx import (
    AttachmentTypes,
    Bot,
    BotShuttingDownError,
    BubbleMarkup,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    KeyboardMarkup,
    OutgoingMessage,
    StatusRecipient,
)
from pybotx.models.attachments import AttachmentVideo

from app.bot.middlewares.db_session import db_session_middleware
from app.db.record.repo import RecordRepo
from app.resources import strings
from app.services.answer_error import AnswerError, AnswerMessageError

collector = HandlerCollector()


@collector.command("/_test-redis-callback-repo", visible=False)
async def test_redis_callback_repo(message: IncomingMessage, bot: Bot) -> None:
    """Testing redis callback."""
    await bot.answer_message("Hello!", callback_timeout=0.1)


@collector.command("/_test-redis-callback-repo-wait", visible=False)
async def test_redis_callback_repo_wait(message: IncomingMessage, bot: Bot) -> None:
    """Testing redis wait callback."""
    sync_id = await bot.answer_message(
        "Hello!", callback_timeout=0.1, wait_callback=False
    )
    await bot.wait_botx_method_callback(sync_id)


@collector.command("/_test-redis-callback-repo-no-wait", visible=False)
async def test_redis_callback_repo_not_wait(message: IncomingMessage, bot: Bot) -> None:
    """Testing redis repo callback not wait."""
    await bot.answer_message("Hello!", callback_timeout=0, wait_callback=False)


@collector.command("/_test-answer-message-error", visible=False)
async def test_answer_message_error(message: IncomingMessage, bot: Bot) -> None:
    """Testing AnswerMessageError error exception."""
    raise AnswerMessageError(
        "test",
        metadata={"test": 1},
        bubbles=BubbleMarkup([[]]),
        keyboard=KeyboardMarkup([[]]),
        file=AttachmentVideo(
            type=AttachmentTypes.VIDEO,
            filename="test_file.mp4",
            size=len(b"Hello, world!\n"),
            is_async_file=False,
            content=b"Hello, world!\n",
            duration=10,
        ),
        recipients=[message.sender.huid],
        silent_response=False,
        markup_auto_adjust=False,
        stealth_mode=False,
        send_push=False,
        ignore_mute=False,
        wait_callback=True,
        callback_timeout=1,
    )


@collector.command("/_test-answer-error", visible=False)
async def test_answer_error(message: IncomingMessage, bot: Bot) -> None:
    """Testing AnswerError exception."""
    raise AnswerError(
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body="test",
            metadata={"test": 1},
            bubbles=BubbleMarkup([[]]),
            keyboard=KeyboardMarkup([[]]),
            file=AttachmentVideo(
                type=AttachmentTypes.VIDEO,
                filename="test_file.mp4",
                size=len(b"Hello, world!\n"),
                is_async_file=False,
                content=b"Hello, world!\n",
                duration=10,
            ),
            recipients=[message.sender.huid],
            silent_response=False,
            markup_auto_adjust=False,
            stealth_mode=False,
            send_push=False,
            ignore_mute=False,
        ),
        wait_callback=True,
        callback_timeout=1,
    )


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
