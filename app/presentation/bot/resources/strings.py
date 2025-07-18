"""Text and templates for messages and api responses."""

from typing import Any, Protocol, cast

from mako.lookup import TemplateLookup  # type: ignore[import-untyped]


class FormatTemplate(Protocol):
    """
    Protocol for correct templates typing.

    Allow use format() instead of render() method that needed to maintain consistency
    with regular string formatting.
    """

    def format(self, **kwargs: Any) -> str:
        """Render template."""


class TemplateFormatterLookup(TemplateLookup):
    """Represent a collection of templates from the local filesystem."""

    def get_template(self, uri: str) -> FormatTemplate:
        """Cast default mako template to FormatTemplate."""

        def _format(**kwargs: Any) -> str:
            return template.render(**kwargs).rstrip()

        template = super().get_template(uri)
        template.format = _format
        return cast(FormatTemplate, template)


lookup = TemplateFormatterLookup(
    directories=[
        "app/presentation/bot/resources/templates/common",
        "app/presentation/bot/resources/templates/sample_record",
    ],
    input_encoding="utf-8",
    strict_undefined=True,
)

BOT_PROJECT_NAME = "template_bot"
BOT_DISPLAY_NAME = "template_bot"

CHAT_CREATED_TEMPLATE = lookup.get_template("chat_created.txt.mako")
HELP_COMMAND_MESSAGE_TEMPLATE = lookup.get_template("help.txt.mako")
HELP_COMMAND_DESCRIPTION = "Показать список команд"
HELP_LABEL = "/help"

# Warnings
OTHER_CTS_WARNING = "\n".join(
    [
        "Данный бот зарегистрирован на другом CTS.",
        "Обратитесь к администратору, чтобы он зарегистрировал бота на вашем CTS",
    ]
)

OTHER_CTS_WITH_BOT_MENTION_WARNING = "\n".join(
    [
        "Данный бот зарегистрирован на другом CTS.",
        "Перейдите по `меншну`, чтобы попасть к вашему боту",
    ]
)

SOMETHING_GOES_WRONG = lookup.get_template("something_goes_wrong.txt.mako")

SAMPLE_RECORD_CREATED_ANSWER = lookup.get_template(
    "sample_record_created_answer.txt.mako"
)
