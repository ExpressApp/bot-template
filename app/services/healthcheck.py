"""Healthcheck service bot."""

from typing import List

from app.domain.entities.healthcheck import (
    HealthCheckServiceResult,
    HealthCheckStatuses,
)
from app.presentation.api.schemas.healthcheck import (
    HealthCheckSucceed,
    HealthCheckFailed,
    HealthCheckResult,
    HealthCheckResponse,
)


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
