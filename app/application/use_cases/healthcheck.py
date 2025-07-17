from app.application.service.interfaces import HealthCheckService
from app.domain.entities.healthcheck import (
    HealthCheckStatuses,
    HealthCheckServiceResult,
)


class HealthCheckUseCase:
    def __init__(self, services: list[tuple[str, HealthCheckService]]):
        self.services = services

    async def execute(
        self,
    ) -> tuple[HealthCheckStatuses, list[HealthCheckServiceResult]]:
        results = []
        healthy = True

        for name, service in self.services:
            error = await service.check()
            results.append(HealthCheckServiceResult(name=name, error=error))
            if error:
                healthy = False

        status = HealthCheckStatuses.OK if healthy else HealthCheckStatuses.ERROR
        return status, results
