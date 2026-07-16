"""Health check endpoints."""

from datetime import datetime
from fastapi import APIRouter
from loguru import logger

from app.core.dependencies import SettingsDep
from app.infrastructure.monitoring.resource_monitor import ResourceMonitor
from app.presentation.api.v1.schemas.common import HealthResponse, SystemInfoResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns basic application health status.
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version,
    )


@router.get("/system", response_model=SystemInfoResponse)
async def system_info() -> SystemInfoResponse:
    """
    System information endpoint.
    
    Returns system resource usage statistics.
    """
    logger.info("System info requested")
    monitor = ResourceMonitor()
    stats = monitor.get_all_stats()
    
    return SystemInfoResponse(
        cpu_percent=stats["cpu_percent"],
        memory_percent=stats["memory"]["percent"],
        disk_percent=stats["disk"]["percent"],
    )
