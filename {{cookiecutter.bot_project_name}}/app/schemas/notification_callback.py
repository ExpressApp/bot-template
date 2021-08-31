"""Data structures for notification callbacks."""

from typing import Any, Dict, List, Literal, Union
from uuid import UUID

from pydantic import BaseModel


class SuccessCallback(BaseModel):
    """Callback for successful request."""

    sync_id: UUID
    status: Literal["ok"]
    result: Dict[str, Any] = {}  # noqa: WPS110


class ErrorCallback(BaseModel):
    """Callback for failed request."""

    sync_id: UUID
    status: Literal["error"]
    reason: str
    errors: List[str] = []
    error_data: Dict[str, Any] = {}


BotXCallback = Union[SuccessCallback, ErrorCallback]
