"""Text and templates for messages and api responses."""

from asyncbox.utils.mako import TemplateFormatterLookup

template_lookup = TemplateFormatterLookup(
    directories=["app/resources/templates"], input_encoding="utf-8"
)
template = template_lookup.get_template

CHAT_CREATED_TEMPLATE = template("chat_created.txt.mako")
HELP_COMMAND_MESSAGE_TEMPLATE = template("help.txt.mako")
HELP_COMMAND_DESCRIPTION = "Показать список команд"
HELP_LABEL = "/help"

# Warnings
BOT_CANT_COMMUNICATE_WITH_OTHERS_CTS = (
    "Данный бот зарегистрирован на другом CTS.\n"
    "Для продолжения работы напишите боту со своего CTS.\n"
    "Найти его можно через поиск корпоративных контактов."
)
