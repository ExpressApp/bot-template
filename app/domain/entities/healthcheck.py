from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class HealthCheckServiceResult:
    name: str
    error: Optional[str]


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class HealthCheckStatuses(StrEnum):
    OK = "ok"
    ERROR = "error"
