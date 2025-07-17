from typing import Literal, Union, Optional, List

from pydantic import BaseModel

from app.domain.entities.healthcheck import HealthCheckStatuses


class HealthCheckSucceed(BaseModel):
    name: str
    status: Literal[HealthCheckStatuses.OK] = HealthCheckStatuses.OK


class HealthCheckFailed(BaseModel):
    name: str
    error: str
    status: Literal[HealthCheckStatuses.ERROR] = HealthCheckStatuses.ERROR


HealthCheckResult = Union[HealthCheckSucceed, HealthCheckFailed]


class HealthCheckResponse(BaseModel):
    status: Optional[HealthCheckStatuses]
    services: List[HealthCheckResult]
