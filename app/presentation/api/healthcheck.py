from fastapi import APIRouter, Request

from app.application.use_cases.healthcheck import HealthCheckUseCase
from app.infrastructure.services.healthcheck import (
    PostgresHealthCheck,
    RedisHealthCheck,
    WorkerHealthCheck,
)
from app.presentation.api.schemas.healthcheck import (
    HealthCheckResponse,
    HealthCheckFailed,
    HealthCheckSucceed,
)

router = APIRouter()


@router.get("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck(request: Request):
    services = [
        ("postgres", PostgresHealthCheck(request)),
        ("redis", RedisHealthCheck(request)),
        ("worker", WorkerHealthCheck()),
    ]

    use_case = HealthCheckUseCase(services)
    status, raw_results = await use_case.execute()

    response_models = []
    for r in raw_results:
        if r.error:
            response_models.append(
                HealthCheckFailed(name=r.name, error=r.error, status="error")
            )
        else:
            response_models.append(HealthCheckSucceed(name=r.name, status="ok"))

    return HealthCheckResponse(
        status=status,
        services=response_models,
    )
