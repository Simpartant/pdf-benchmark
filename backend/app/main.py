"""FastAPI Application Entry Point."""

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.cors import setup_cors
from app.core.logging import setup_logging
from app.presentation.api.v1.router import api_router
from app.presentation.middleware.error_handler import error_handler_middleware
from app.presentation.middleware.request_logger import request_logger_middleware
from app.api.routes import router as api_routes


# Global variable to track application start time
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    global app_start_time
    app_start_time = time.time()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create necessary directories
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.results_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("Application directories created")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Results directory: {settings.results_dir}")
    logger.info(f"Logs directory: {settings.logs_dir}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Setup logging first
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API for benchmarking PDF extraction methods",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # Setup CORS
    setup_cors(app)
    logger.info(f"CORS enabled for origins: {settings.cors_origins_list}")
    
    # Add middleware
    app.middleware("http")(request_logger_middleware)
    app.middleware("http")(error_handler_middleware)
    
    # Include routers
    app.include_router(api_router)  # Old presentation layer routes
    app.include_router(api_routes, prefix="/api/v1")  # New API routes
    
    logger.info("Application configured successfully")
    
    return app


# Create app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "api": "/api/v1",
    }
