"""API routes for PDF extraction benchmark."""

import sys
import time
import shutil
import json
import hashlib
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
    get_result_storage,
)
from app.api.schemas import (
    HealthResponse,
    LibrariesResponse,
    LibraryResponse,
    DependencyInfo,
    BenchmarkResponse,
    ExtractionResultResponse,
    HistoryListResponse,
    HistoryResponse,
    DeleteResponse,
)
from app.core.config import settings

router = APIRouter()


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    from app.main import app_start_time

    logger.info("Health check requested")
    uptime = time.time() - app_start_time
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
    Get all available PDF extraction libraries with REAL availability
    and version information (derived from each extractor's dependency
    diagnostics). Missing dependencies are reported as unavailable
    without crashing the app.
    """
    logger.info("Fetching available libraries (real availability)")

    libraries = library_service.get_all_libraries(force_refresh=True)

    library_responses = [
        LibraryResponse(
            name=lib.name,
            display_name=lib.display_name,
            version=lib.version,
            status=lib.status.value,
            installed=(lib.status.value in ("available", "error")),
            description=lib.description,
            capabilities=lib.capabilities,
            performance_notes=lib.performance_notes,
            dependencies=[
                DependencyInfo(
                    name=d.get("name", ""),
                    module=d.get("module", ""),
                    installed=d.get("installed", False),
                    version=d.get("version"),
                    error=d.get("error"),
                )
                for d in (library_service.get_dependency_diagnostics(lib.name) or {}).get(
                    "dependencies", []
                )
            ],
            diagnostics=(library_service.get_dependency_diagnostics(lib.name) or {}).get(
                "diagnostics", []
            ),
        )
        for lib in libraries
    ]

    available = sum(1 for lib in libraries if lib.status.value == "available")
    logger.info(f"Found {len(library_responses)} libraries ({available} installed)")

    return LibrariesResponse(
        libraries=library_responses,
        total=len(library_responses),
    )


@router.post("/extract", response_model=BenchmarkResponse, tags=["Extraction"])
async def extract_pdf(
    benchmark_service: BenchmarkServiceDep,
    file: UploadFile = File(..., description="PDF file to extract"),
    libraries: str = Form(..., description="Comma-separated list of library ids"),
) -> BenchmarkResponse:
    """
    Extract text from uploaded PDF using specified libraries.

    Workflow:
    1. Upload PDF file
    2. Save to temporary location
    3. Run benchmark with specified libraries (docling, unstructured,
       mineru, ...)
    4. Save extraction outputs
    5. Return results with performance metrics
    """
    logger.info(f"PDF upload received: {file.filename}, libraries: {libraries}")

    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    if file.content_type and file.content_type not in ['application/pdf', 'application/x-pdf']:
        logger.warning(f"Unexpected content type: {file.content_type}")

    library_list = [lib.strip() for lib in libraries.split(',') if lib.strip()]
    if not library_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one library must be specified",
        )

    logger.info(f"Parsed libraries: {library_list}")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid4())[:8]
    safe_filename = f"{file_id}_{file.filename}"
    pdf_path = upload_dir / safe_filename

    try:
        logger.info(f"Saving uploaded file to: {pdf_path}")
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = pdf_path.stat().st_size
        logger.info(f"File saved: {pdf_path} ({file_size} bytes)")

        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            pdf_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
            )

        logger.info(f"Starting benchmark for {file.filename} with libraries: {library_list}")
        benchmark_result = benchmark_service.run_benchmark_by_path(
            pdf_path=pdf_path,
            library_names=library_list,
        )

        extraction_responses = [
            ExtractionResultResponse(**result.to_dict())
            for result in benchmark_result.extraction_results
        ]

        # Calculate overall status
        success_count = sum(1 for r in benchmark_result.extraction_results if r.status == "success")
        if success_count == len(library_list):
            overall_status = "completed"
        elif success_count > 0:
            overall_status = "partial"
        else:
            overall_status = "failed"

        # Get file hash from first result
        file_hash = benchmark_result.extraction_results[0].file_hash if benchmark_result.extraction_results else ""

        response = BenchmarkResponse(
            id=str(benchmark_result.id),
            pdf_filename=benchmark_result.pdf_filename,
            pdf_id=str(benchmark_result.pdf_id),
            file_hash=file_hash,
            status=overall_status,
            extraction_results=extraction_responses,
            total_duration_ms=benchmark_result.total_duration_ms,
            fastest_library=benchmark_result.fastest_library,
            most_efficient_memory=benchmark_result.most_efficient_memory,
            most_text_extracted=benchmark_result.most_text_extracted,
            created_at=benchmark_result.created_at,
        )

        logger.info(f"Extraction completed: {overall_status} for {file.filename}")
        logger.info(f"Results: {len(extraction_responses)} libraries, fastest: {response.fastest_library}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )
    finally:
        try:
            if pdf_path and pdf_path.exists():
                pdf_path.unlink()
                logger.debug(f"Cleaned up temp file: {pdf_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {pdf_path}: {e}")


@router.get("/compare/{benchmark_group_id}", response_model=BenchmarkResponse, tags=["Comparison"])
async def get_comparison_by_group(
    benchmark_group_id: UUID,
    result_storage = Depends(get_result_storage),
) -> BenchmarkResponse:
    """
    Get all extraction results for a benchmark group.
    
    This endpoint fetches all runs belonging to the same benchmark group,
    ensuring they share the same input file hash.
    """
    from app.models.extraction_result import ExtractionResult
    
    logger.info(f"GET /compare/{benchmark_group_id}, storage_id: {id(result_storage)}")
    
    try:
        stored_data = result_storage.load_by_benchmark_group_id(benchmark_group_id)
    except FileNotFoundError:
        logger.warning(f"Benchmark group not found: {benchmark_group_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark group not found: {benchmark_group_id}",
        )
    
    extraction_responses = [
        ExtractionResultResponse(**ExtractionResult.from_dict(res).to_dict())
        for res in stored_data.get("extraction_results", [])
    ]
    
    # Calculate overall status
    success_count = sum(1 for r in stored_data.get("extraction_results", []) if r.get("status") == "success")
    if success_count == len(stored_data.get("extraction_results", [])):
        overall_status = "completed"
    elif success_count > 0:
        overall_status = "partial"
    else:
        overall_status = "failed"
    
    return BenchmarkResponse(
        id=stored_data.get("benchmark_id", str(benchmark_group_id)),
        pdf_filename=stored_data.get("pdf_filename", ""),
        pdf_id=stored_data.get("pdf_id", ""),
        file_hash=stored_data.get("file_hash", ""),
        status=overall_status,
        extraction_results=extraction_responses,
        total_duration_ms=stored_data.get("total_duration_ms", 0),
        fastest_library=stored_data.get("summary", {}).get("fastest_library"),
        most_efficient_memory=stored_data.get("summary", {}).get("most_efficient_memory"),
        most_text_extracted=stored_data.get("summary", {}).get("most_text_extracted"),
        created_at=datetime.fromisoformat(stored_data["created_at"]) if isinstance(stored_data.get("created_at"), str) else datetime.now(),
    )


@router.get("/history", response_model=HistoryListResponse, tags=["History"])
async def get_history(
    history_service: HistoryServiceDep,
) -> HistoryListResponse:
    """Get extraction history by scanning result directories."""
    logger.info("Fetching extraction history from result directories")

    history_records = history_service.get_all_history()

    history_responses = []
    for record in history_records:
        if record.success_count > 0 and record.failure_count == 0:
            status_val = "success"
        elif record.success_count > 0 and record.failure_count > 0:
            status_val = "partial"
        else:
            status_val = "failed"

        selected_library = record.libraries_used[0] if record.libraries_used else "unknown"

        try:
            peak_memory = 0.0
            avg_cpu = 0.0
            page_count = 0
            output_size = 0
            benchmark_group_id = str(record.benchmark_result_id)

            for result_dir in history_service._scan_result_directories():
                try:
                    history_record = history_service._load_history_from_dir(result_dir)
                    if history_record and history_record.id == record.id:
                        benchmark_file = result_dir / "benchmark.json"
                        if benchmark_file.exists():
                            with open(benchmark_file, "r") as f:
                                benchmark_data = json.load(f)

                            extraction_results = benchmark_data.get("extraction_results", [])
                            successful_results = [r for r in extraction_results if r.get("status") == "success"]

                            if successful_results:
                                peak_memory = max(
                                    r.get("peakMemoryMb", r.get("peak_memory_mb", 0))
                                    for r in successful_results
                                )
                                cpu_values = [
                                    r.get("averageCpuPercent", r.get("cpu_usage_percent", 0))
                                    for r in successful_results
                                ]
                                avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
                                page_count = successful_results[0].get("pageCount", successful_results[0].get("pages_extracted", 0))
                                output_size = sum(r.get("outputSizeBytes", r.get("output_size_bytes", 0)) for r in successful_results)
                                benchmark_group_id = benchmark_data.get("benchmarkGroupId", str(record.benchmark_result_id))
                        break
                except Exception as e:
                    logger.debug(f"Could not load metrics for {result_dir}: {e}")
                    continue

            history_responses.append(
                HistoryResponse(
                    runId=str(record.id),
                    benchmarkGroupId=benchmark_group_id,
                    filename=record.pdf_filename,
                    createdAt=record.created_at,
                    selectedLibrary=selected_library,
                    status=status_val,
                    processingTime=record.total_duration_ms,
                    peakMemory=peak_memory,
                    averageCpu=avg_cpu,
                    pageCount=page_count,
                    outputSize=output_size,
                )
            )
        except Exception as e:
            logger.warning(f"Failed to process history record {record.id}: {e}")
            continue

    logger.info(f"Found {len(history_responses)} history records")
    return HistoryListResponse(history=history_responses, total=len(history_responses))


@router.get("/history/{history_id}", response_model=BenchmarkResponse, tags=["History"])
async def get_benchmark_result(
    history_id: UUID,
    history_service: HistoryServiceDep,
) -> BenchmarkResponse:
    """Get full benchmark result by history ID."""
    from app.models.extraction_result import ExtractionResult

    logger.info(f"Fetching benchmark result for history: {history_id}")

    history_record = history_service.get_history_by_id(history_id)
    if not history_record:
        logger.warning(f"History record not found: {history_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record not found: {history_id}",
        )

    result_storage = get_result_storage()

    try:
        stored_data = result_storage.load_by_benchmark_id(history_record.benchmark_result_id)
        extraction_responses = [
            ExtractionResultResponse(**ExtractionResult.from_dict(res).to_dict())
            for res in stored_data.get("extraction_results", [])
        ]

        # Calculate overall status
        success_count = sum(1 for r in stored_data.get("extraction_results", []) if r.get("status") == "success")
        if success_count == len(stored_data.get("extraction_results", [])):
            overall_status = "completed"
        elif success_count > 0:
            overall_status = "partial"
        else:
            overall_status = "failed"

        return BenchmarkResponse(
            id=stored_data.get("benchmark_id", str(history_id)),
            pdf_filename=stored_data.get("pdf_filename", history_record.pdf_filename),
            pdf_id=stored_data.get("pdf_id", str(history_record.pdf_id)),
            file_hash=stored_data.get("file_hash", ""),
            status=overall_status,
            extraction_results=extraction_responses,
            total_duration_ms=stored_data.get("total_duration_ms", history_record.total_duration_ms),
            fastest_library=stored_data.get("summary", {}).get("fastest_library"),
            most_efficient_memory=stored_data.get("summary", {}).get("most_efficient_memory"),
            most_text_extracted=stored_data.get("summary", {}).get("most_text_extracted"),
            created_at=datetime.fromisoformat(stored_data["created_at"]) if isinstance(stored_data.get("created_at"), str) else datetime.now(),
        )
    except FileNotFoundError:
        logger.warning(f"Stored result not found for benchmark {history_record.benchmark_result_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark result data not found on disk",
        )


@router.delete("/history/{history_id}", response_model=DeleteResponse, tags=["History"])
async def delete_history(
    history_id: UUID,
    history_service: HistoryServiceDep,
) -> DeleteResponse:
    """Delete extraction history record by ID."""
    logger.info(f"Deleting history record: {history_id}")

    success = history_service.delete_history(history_id)
    if not success:
        logger.warning(f"History record not found: {history_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record not found: {history_id}",
        )

    logger.info(f"History record deleted successfully: {history_id}")
    return DeleteResponse(success=True, message=f"History record {history_id} deleted successfully")
