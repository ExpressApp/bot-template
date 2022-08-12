"""Handlers for default bot commands and system events."""

from os import environ

from pybotx import (
    Bot,
    BubbleMarkup,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    StatusRecipient,
)

from app.resources import strings

collector = HandlerCollector()


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
