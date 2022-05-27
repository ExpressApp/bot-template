"""Endpoint healthcheck."""

from typing import Optional

from fastapi import APIRouter

from app.api.dependencies.healthcheck import (
    check_db_connection_dependency,
    check_redis_connection_dependency,
)
from app.services.healthcheck import (
    HealthCheckResponse,
    HealthCheckResponseBuilder,
    HealthCheckServiceResult,
)

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck(
    redis_connection_error: Optional[str] = check_redis_connection_dependency,
    db_connection_error: Optional[str] = check_db_connection_dependency,
) -> HealthCheckResponse:
    """Check the health of the bot and services."""
    healthcheck_builder = HealthCheckResponseBuilder()
    healthcheck_builder.add_healthcheck_result(
        HealthCheckServiceResult(name="postgres", error=db_connection_error)
    )
    healthcheck_builder.add_healthcheck_result(
        HealthCheckServiceResult(name="redis", error=redis_connection_error)
    )

    return healthcheck_builder.build()
