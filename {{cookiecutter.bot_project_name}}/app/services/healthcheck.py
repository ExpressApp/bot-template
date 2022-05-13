"""Healthcheck service bot."""
from dataclasses import dataclass
from typing import List, Literal, Optional, Union

from pydantic import BaseModel

from app.schemas.enums import HealthCheckStatuses


@dataclass
class HealthCheckServiceResult:
    name: str
    error: Optional[str]


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


class HealthCheckResponseBuilder:
    def __init__(self) -> None:
        self._healthcheck_results: List[HealthCheckServiceResult] = []

    def add_healthcheck_result(self, service: HealthCheckServiceResult) -> None:
        self._healthcheck_results.append(service)

    def build(self) -> HealthCheckResponse:
        healthcheck: HealthCheckResult
        healthchecks = []
        healthy = True
        for healthcheck_result in self._healthcheck_results:
            if healthcheck_result.error is None:
                healthcheck = HealthCheckSucceed(name=healthcheck_result.name)
            else:
                healthy = False
                healthcheck = HealthCheckFailed(
                    name=healthcheck_result.name, error=healthcheck_result.error
                )
            healthchecks.append(healthcheck)

        result_status = HealthCheckStatuses.OK if healthy else HealthCheckStatuses.ERROR
        return HealthCheckResponse(status=result_status, services=healthchecks)
