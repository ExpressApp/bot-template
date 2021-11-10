"""Handlers for default bot commands and system events."""

from os import environ

from botx import Bot, Collector, Message, SendingMessage

from app.bot.dependencies.db import session_factory_dependency
from app.db.repos.record_repo import RecordRepo
from app.db.sqlalchemy import AsyncSessionFactory
from app.resources import strings

collector = Collector()


@collector.default(include_in_status=False)
async def default_handler(
    message: Message,
    session_factory: AsyncSessionFactory = session_factory_dependency,
) -> None:
    """Run if command not found."""
    # add text to history
    # example of using database
    async with session_factory() as session, session.begin():
        record_repo = RecordRepo(session)

        await record_repo.create_record(text=message.body)


@collector.chat_created
async def chat_created(
    message: Message,
    bot: Bot,
) -> None:
    """Send a welcome message and the bot functionality in new created chat."""
    text = strings.CHAT_CREATED_TEMPLATE.format(
        bot_project_name=strings.BOT_DISPLAY_NAME
    )
    reply = SendingMessage.from_message(text=text, message=message)
    reply.add_bubble(command=bot.command_for("help"), label=strings.HELP_LABEL)
    await bot.send(reply)


@collector.handler(
    command="/help", name="help", description=strings.HELP_COMMAND_DESCRIPTION
)
async def show_help(message: Message, bot: Bot) -> None:
    """Справка по командам."""
    status = await message.bot.status()

    # For each public command:
    # * collect full description or
    # * collect short description like in status or
    # * skip command without any description
    commands = []
    for command in status.result.commands:
        command_handler = message.bot.handler_for(command.name)
        description = command_handler.full_description or command_handler.description
        if description:
            commands.append((command.body, description))

    text = strings.HELP_COMMAND_MESSAGE_TEMPLATE.format(commands=commands)
    await bot.answer_message(text, message)


@collector.hidden(command="/_debug:git-commit-sha")
async def git_commit_sha(message: Message, bot: Bot) -> None:
    """Show git commit SHA."""
    await bot.answer_message(environ.get("GIT_COMMIT_SHA", "<undefined>"), message)


@collector.hidden(command="/_history")
async def history(
    message: Message,
    bot: Bot,
    session_factory: AsyncSessionFactory = session_factory_dependency,
) -> None:
    """Show history of unhandled messages."""
    async with session_factory() as session, session.begin():
        record_repo = RecordRepo(session)
        records = await record_repo.get_all()

    text = "\n".join(row.record_data for row in records)
    await bot.answer_message(text, message)
