"""API v1 main router."""

from fastapi import APIRouter

from .endpoints import health

# Create API v1 router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(health.router)
