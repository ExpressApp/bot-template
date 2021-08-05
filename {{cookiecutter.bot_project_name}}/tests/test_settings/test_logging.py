from copy import deepcopy
from typing import List

import pytest
from botx import AttachList
from botx.testing import MessageBuilder
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from app.settings.logger import (
    MAX_FILE_LENGTH,
    format_botx_client_payload,
    format_record,
    trim_attachments_content,
)

image_content = (
    "data:image/gif;base64,R0lGODdhMAAwAPAAAAAAAP///ywAAAAAMAAw"
    "AAAC8IyPqcvt3wCcDkiLc7C0qwyGHhSWpjQu5yqmCYsapyuvUUlvONmOZtfzgFz"
    "ByTB10QgxOR0TqBQejhRNzOfkVJ+5YiUqrXF5Y5lKh/DeuNcP5yLWGsEbtLiOSp"
    "a/TPg7JpJHxyendzWTBfX0cxOnKPjgBzi4diinWGdkF8kjdfnycQZXZeYGejmJl"
    "ZeGl9i2icVqaNVailT6F5iJ90m6mvuTS4OK05M0vDk0Q4XUtwvKOzrcd3iq9uis"
    "F81M1OIcR7lEewwcLp7tuNNkM3uNna3F2JQFo97Vriy/Xl4/f1cf5VWzXyym7PH"
    "hhx4dbgYKAAA7"
)


@pytest.fixture
def attachments() -> List[dict]:
    return [
        {"data": {"content": image_content, "file_name": "test.gif"}, "type": "image"}
    ]


def test_trim_attachments_content(attachments: List[dict]):
    trimmed_attachments = trim_attachments_content(attachments)
    assert (
        trimmed_attachments[0]["data"]["content"]
        == "data:image/gif;base64,R0lGODdhMAAwAPAAAA...<trimmed>"
    )


def test_custom_formatter():
    record_dict = {"extra": {}}
    assert format_record(record_dict) == LOGURU_FORMAT + "{exception}\n"

    record_dict = {"extra": {"payload": {}}}
    assert "extra[payload]" in format_record(record_dict)

    incoming_request = {
        "method": "POST",
        "url": "https://cts.example.ru/api/v3/botx/command/callback",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        },
        "query_params": {},
        "request_data": '{"sync_id": "uuid", "recipients": "all", "command_result": {"status": "ok", "body": "", "metadata": {}, "keyboard": [], "bubble": [], "mentions": []}, "file": {"file_name": "d.txt", "data": "data:text/plain;base64, foobar'
        '="}, "opts": {"stealth_mode": false, "notification_opts": {"send": true, "force_dnd": false}}}'.replace(
            "foobar", "foobar" * MAX_FILE_LENGTH * 2
        ),
    }
    format_botx_client_payload(incoming_request)
    file_data = incoming_request["request_data"]["file"]["data"]
    assert file_data.rfind("foobar" * MAX_FILE_LENGTH) == file_data.find(
        "foobar" * MAX_FILE_LENGTH
    )


def test_message_immutability_after_logging(attachments: List[dict]):
    attach_list = AttachList(__root__=attachments)
    builder = MessageBuilder(attachments=attach_list)

    message = (builder.message).dict()
    copied_message = deepcopy(message)

    logger.bind(botx_bot=True, payload=message).debug("process incoming message")
    assert message == copied_message
