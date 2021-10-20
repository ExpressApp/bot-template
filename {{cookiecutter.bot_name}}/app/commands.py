"""Handlers for default bot commands and system events."""

from botx import Bot, Collector, Message, SendingMessage

from app.resources import strings

collector = Collector()


@collector.default(include_in_status=False)
async def default_handler() -> None:
    """Run if command not found."""


@collector.chat_created
async def chat_created(message: Message, bot: Bot) -> None:
    """Send a welcome message and the bot functionality in new created chat."""
    text = strings.CHAT_CREATED_TEMPLATE.format(bot_name=bot.state.bot_name)
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
