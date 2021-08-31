"""Data structures for notification callbacks."""

from types import MappingProxyType
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, DictError

from app.schemas.enums import StrEnum


class StatusEnum(StrEnum):
    """Status values Enum."""

    ok = "ok"
    error = "error"


class BaseCallback(BaseModel):
    """Base class for notification callbacks."""

    sync_id: UUID
    status: StatusEnum

    @classmethod
    def validate(cls: BaseModel, value: Any) -> "BaseCallback":  # noqa: WPS110
        try:
            value_as_dict = dict(value)
        except (TypeError, ValueError) as exc:
            raise DictError() from exc
        result_cls = _type_map[value_as_dict["status"]]
        return result_cls(**value_as_dict)  # type: ignore


class SuccessCallback(BaseCallback):
    """Callback for successful request."""

    result: Dict[str, Any] = {}  # noqa: WPS110


class ErrorCallback(BaseCallback):
    """Callback for failed request."""

    reason: str
    errors: List[str] = []
    error_data: Dict[str, Any] = {}


_type_map = MappingProxyType(
    {
        StatusEnum.error: ErrorCallback,
        StatusEnum.ok: SuccessCallback,
    }
)
