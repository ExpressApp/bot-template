"""Configuration of routers for all endpoints."""
from fastapi import APIRouter

from app.api.endpoints.botx import router as bot_router
from app.api.endpoints.healthcheck import router as healthcheck_router

router = APIRouter()

router.include_router(healthcheck_router)
router.include_router(bot_router)
