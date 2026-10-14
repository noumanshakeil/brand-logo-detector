from fastapi import APIRouter
from backend.api import health, brands, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(brands.router, prefix="/api", tags=["brands"])
api_router.include_router(ui.router, tags=["ui"])
