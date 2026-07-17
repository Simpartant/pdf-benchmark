"""API routes for PDF extraction benchmark."""

import sys
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from loguru import logger

from app.api.dependencies import (
    LibraryServiceDep,
    BenchmarkServiceDep,
    HistoryServiceDep,
    get_benchmark_service,
)
from app.api.schemas import (
    HealthResponse,
    LibrariesResponse,
    LibraryResponse,
    BenchmarkResponse,
    ExtractionResultResponse,
    HistoryListResponse,
    HistoryResponse,
    DeleteResponse,
)
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns application health status and version information.
    """
    from app.main import app_start_time
    
    logger.info("Health check requested")
    
    # Calculate uptime
    uptime = time.time() - app_start_time
    
    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        python_version=python_version,
        uptime=uptime,
    )


@router.get("/libraries", response_model=LibrariesResponse, tags=["Libraries"])
async def get_libraries(
    library_service: LibraryServiceDep,
) -> LibrariesResponse:
    """
    Get all available PDF extraction libraries.
    
    Returns information about each library including:
    - Installation status
    - Version information
    - Capabilities
    - Performance notes
    """
    logger.info("Fetching available libraries")
    
    libraries = library_service.get_all_libraries(force_refresh=True)
    
    library_responses = [
        LibraryResponse(
            name=lib.name,
            display_name=lib.display_name,
            installed=(lib.status.value == "available"),
            version=lib.version,
            status=lib.status.value,
            description=lib.description,
            capabilities=lib.capabilities,
            performance_notes=lib.performance_notes,
        )
        for lib in libraries
    ]
    
    logger.info(f"Found {len(library_responses)} libraries ({sum(1 for lib in libraries if lib.status.value == 'available')} installed)")
    
    return LibrariesResponse(
        libraries=library_responses,
        total=len(library_responses),
    )


@router.post("/extract", response_model=BenchmarkResponse, tags=["Extraction"])
async def extract_pdf(
    file: UploadFile = File(..., description="PDF file to extract"),
    libraries: str = Form(..., description="Comma-separated list of library names"),
    benchmark_service: BenchmarkServiceDep = None,
) -> BenchmarkResponse:
    """
    Extract text from uploaded PDF using specified libraries.
    
    Workflow:
    1. Upload PDF file
    2. Save to temporary location
    3. Run benchmark with specified libraries (including Docling)
    4. Save extraction outputs
    5. Return results with performance metrics
    
    Args:
        file: Uploaded PDF file
        libraries: Comma-separated library names (e.g., "docling,pypdf,pdfplumber")
        benchmark_service: Benchmark service dependency
        
    Returns:
        Benchmark results with extraction data and performance metrics
        
    Raises:
        HTTPException: If file validation fails or extraction fails
    """
    logger.info(f"PDF upload received: {file.filename}, libraries: {libraries}")
    
    # Validate file is PDF
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )
    
    # Validate content type
    if file.content_type and file.content_type not in ['application/pdf', 'application/x-pdf']:
        logger.warning(f"Unexpected content type: {file.content_type}")
    
    # Parse library names
    library_list = [lib.strip() for lib in libraries.split(',') if lib.strip()]
    if not library_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one library must be specified",
        )
    
    logger.info(f"Parsed libraries: {library_list}")
    
    # Create upload directory if not exists
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    file_id = str(uuid4())[:8]
    safe_filename = f"{file_id}_{file.filename}"
    pdf_path = upload_dir / safe_filename
    
    try:
        # Save uploaded file
        logger.info(f"Saving uploaded file to: {pdf_path}")
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = pdf_path.stat().st_size
        logger.info(f"File saved: {pdf_path} ({file_size} bytes)")
        
        # Validate file size
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            # Clean up file
            pdf_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
            )
        
        # Run benchmark with all specified libraries
        logger.info(f"Starting benchmark for {file.filename} with libraries: {library_list}")
        benchmark_result = benchmark_service.run_benchmark_by_path(
            pdf_path=pdf_path,
            library_names=library_list,
        )
        
        # Convert to response
        extraction_responses = [
            ExtractionResultResponse(
                id=str(result.id),
                library_name=result.library_name,
                success=result.success,
                text_content=result.text_content,
                execution_time_ms=result.execution_time_ms,
                memory_usage_mb=result.memory_usage_mb,
                cpu_usage_percent=result.cpu_usage_percent,
                pages_extracted=result.pages_extracted,
                char_count=result.char_count,
                word_count=result.word_count,
                error_message=result.error_message,
                # Comprehensive output metrics
                output_size_bytes=result.output_size_bytes,
                images_count=result.images_count,
                tables_count=result.tables_count,
                markdown_length=result.markdown_length,
                json_size_bytes=result.json_size_bytes,
                output_directory=result.output_directory,
                extracted_at=result.extracted_at,
            )
            for result in benchmark_result.extraction_results
        ]
        
        response = BenchmarkResponse(
            id=str(benchmark_result.id),
            pdf_filename=benchmark_result.pdf_filename,
            pdf_id=str(benchmark_result.pdf_id),
            extraction_results=extraction_responses,
            total_duration_ms=benchmark_result.total_duration_ms,
            fastest_library=benchmark_result.fastest_library,
            most_efficient_memory=benchmark_result.most_efficient_memory,
            most_text_extracted=benchmark_result.most_text_extracted,
            created_at=benchmark_result.created_at,
        )
        
        logger.info(f"Extraction completed successfully for {file.filename}")
        logger.info(f"Results: {len(extraction_responses)} libraries, fastest: {response.fastest_library}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )
        
    finally:
        # Clean up uploaded file
        try:
            if pdf_path and pdf_path.exists():
                pdf_path.unlink()
                logger.debug(f"Cleaned up temp file: {pdf_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {pdf_path}: {e}")


@router.get("/history", response_model=HistoryListResponse, tags=["History"])
async def get_history(
    history_service: HistoryServiceDep,
) -> HistoryListResponse:
    """
    Get extraction history.
    
    Returns all historical extraction records including:
    - PDF filename
    - Libraries used
    - Duration
    - Success/failure counts
    - Timestamps
    """
    logger.info("Fetching extraction history")
    
    history_records = history_service.get_all_history()
    
    history_responses = [
        HistoryResponse(
            id=str(record.id),
            pdf_filename=record.pdf_filename,
            pdf_id=str(record.pdf_id),
            libraries_used=record.libraries_used,
            total_duration_ms=record.total_duration_ms,
            success_count=record.success_count,
            failure_count=record.failure_count,
            benchmark_result_id=str(record.benchmark_result_id),
            created_at=record.created_at,
        )
        for record in history_records
    ]
    
    logger.info(f"Found {len(history_responses)} history records")
    
    return HistoryListResponse(
        history=history_responses,
        total=len(history_responses),
    )


@router.delete("/history/{history_id}", response_model=DeleteResponse, tags=["History"])
async def delete_history(
    history_id: UUID,
    history_service: HistoryServiceDep,
) -> DeleteResponse:
    """
    Delete extraction history record by ID.
    
    Args:
        history_id: UUID of history record to delete
        
    Returns:
        Success status and message
        
    Raises:
        HTTPException: If history record not found
    """
    logger.info(f"Deleting history record: {history_id}")
    
    success = history_service.delete_history(history_id)
    
    if not success:
        logger.warning(f"History record not found: {history_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record not found: {history_id}",
        )
    
    logger.info(f"History record deleted successfully: {history_id}")
    
    return DeleteResponse(
        success=True,
        message=f"History record {history_id} deleted successfully",
    )
