"""Request logging middleware."""

import time
from fastapi import Request
from loguru import logger


async def request_logger_middleware(request: Request, call_next):
    """
    Request logging middleware.
    
    Logs all incoming requests with method, path, and execution time.
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate execution time
    execution_time = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Time: {execution_time:.2f}ms"
    )
    
    return response
