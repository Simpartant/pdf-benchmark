"""Dependency injection for API endpoints."""

from typing import Annotated
from fastapi import Depends

from app.services.library_service import LibraryService
from app.services.extraction_service import ExtractionService
from app.services.history_service import HistoryService
from app.benchmark.benchmark_service import BenchmarkService
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.benchmark.result_storage import ResultStorageService


# Service instances (singleton pattern)
_library_service: LibraryService | None = None
_extraction_service: ExtractionService | None = None
_history_service: HistoryService | None = None
_benchmark_service: BenchmarkService | None = None
_benchmark_engine: BenchmarkEngine | None = None
_result_storage: ResultStorageService | None = None


def get_benchmark_engine() -> BenchmarkEngine:
    """
    Get or create BenchmarkEngine instance.
    
    Returns:
        BenchmarkEngine singleton instance
    """
    global _benchmark_engine
    if _benchmark_engine is None:
        _benchmark_engine = BenchmarkEngine(sampling_interval_ms=50)
    return _benchmark_engine


def get_result_storage() -> ResultStorageService:
    """
    Get or create ResultStorageService instance.
    
    Returns:
        ResultStorageService singleton instance
    """
    global _result_storage
    if _result_storage is None:
        _result_storage = ResultStorageService()
    return _result_storage


def get_library_service() -> LibraryService:
    """
    Get or create LibraryService instance.
    
    Returns:
        LibraryService singleton instance
    """
    global _library_service
    if _library_service is None:
        _library_service = LibraryService()
    return _library_service


def get_extraction_service() -> ExtractionService:
    """
    Get or create ExtractionService instance.
    
    Returns:
        ExtractionService singleton instance
    """
    global _extraction_service
    if _extraction_service is None:
        benchmark_engine = get_benchmark_engine()
        _extraction_service = ExtractionService(benchmark_engine=benchmark_engine)
    return _extraction_service


def get_history_service() -> HistoryService:
    """
    Get or create HistoryService instance.
    
    Returns:
        HistoryService singleton instance
    """
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service


def get_benchmark_service(
    extraction_service: Annotated[ExtractionService, Depends(get_extraction_service)],
    history_service: Annotated[HistoryService, Depends(get_history_service)],
    result_storage: Annotated[ResultStorageService, Depends(get_result_storage)],
) -> BenchmarkService:
    """
    Get or create BenchmarkService instance with dependencies.
    
    Args:
        extraction_service: ExtractionService dependency
        history_service: HistoryService dependency
        result_storage: ResultStorageService dependency
        
    Returns:
        BenchmarkService singleton instance
    """
    global _benchmark_service
    if _benchmark_service is None:
        _benchmark_service = BenchmarkService(
            extraction_service=extraction_service,
            history_service=history_service,
            result_storage=result_storage,
        )
    return _benchmark_service


# Type aliases for dependency injection
LibraryServiceDep = Annotated[LibraryService, Depends(get_library_service)]
ExtractionServiceDep = Annotated[ExtractionService, Depends(get_extraction_service)]
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
BenchmarkServiceDep = Annotated[BenchmarkService, Depends(get_benchmark_service)]
