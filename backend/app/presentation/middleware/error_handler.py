"""Error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware.
    
    Catches all unhandled exceptions and returns a JSON response.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
