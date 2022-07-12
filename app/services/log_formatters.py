"""Helpers to format log messages in smart logger wrapper."""

from pprint import pformat
from typing import Any, Dict, Optional

from pybotx.logger import trim_file_data_in_incoming_json

from app.logger import logger


def format_raw_command(raw_command: Optional[Dict[str, Any]]) -> str:
    if raw_command is None:
        logger.warning("Empty `raw_command`")
        return "<empty `raw_command`>"

    trimmed_raw_command = trim_file_data_in_incoming_json(raw_command)
    return pformat(trimmed_raw_command)
