"""Configuration of routers for all endpoints."""
from fastapi import APIRouter

from app.api.endpoints.botx import router as bot_router

router = APIRouter()

router.include_router(bot_router, tags=["botx"])
