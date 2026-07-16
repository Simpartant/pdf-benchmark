"""Benchmark service for running PDF extraction benchmarks."""

from pathlib import Path
from typing import List
from uuid import UUID

from app.models.benchmark_result import BenchmarkResult
from app.models.document import PDFDocument
from app.services.extraction_service import ExtractionService
from app.services.history_service import HistoryService
from app.benchmark.result_storage import ResultStorageService
from loguru import logger


class BenchmarkService:
    """Service for running and managing benchmarks with result storage."""

    def __init__(
        self,
        extraction_service: ExtractionService,
        history_service: HistoryService,
        result_storage: ResultStorageService = None,
    ):
        """
        Initialize benchmark service.
        
        Args:
            extraction_service: Service for PDF extraction
            history_service: Service for history management
            result_storage: Service for storing results to disk
        """
        self.extraction_service = extraction_service
        self.history_service = history_service
        self.result_storage = result_storage or ResultStorageService()

    def run_benchmark(
        self,
        pdf_document: PDFDocument,
        library_names: List[str],
    ) -> BenchmarkResult:
        """
        Run benchmark on PDF with multiple libraries.
        
        Args:
            pdf_document: PDFDocument to benchmark
            library_names: List of library names to use
            
        Returns:
            BenchmarkResult with all extraction results
        """
        logger.info(
            f"Starting benchmark for {pdf_document.filename} "
            f"with libraries: {library_names}"
        )

        pdf_path = Path(pdf_document.file_path)

        # Extract with all libraries
        extraction_results = self.extraction_service.extract_with_multiple_libraries(
            pdf_path=pdf_path,
            library_names=library_names,
        )

        # Create benchmark result
        benchmark_result = BenchmarkResult(
            pdf_filename=pdf_document.filename,
            pdf_id=pdf_document.id,
            extraction_results=extraction_results,
        )

        # Calculate summary
        benchmark_result.calculate_summary()

        # Save to history
        self.history_service.add_history(benchmark_result)

        # Store results to disk
        try:
            result_dir = self.result_storage.store_benchmark_result(benchmark_result)
            logger.info(f"Results stored to: {result_dir}")
        except Exception as e:
            logger.error(f"Failed to store results: {e}")

        logger.info(
            f"Benchmark completed for {pdf_document.filename}, "
            f"fastest: {benchmark_result.fastest_library}"
        )

        return benchmark_result

    def run_benchmark_by_path(
        self,
        pdf_path: Path,
        library_names: List[str],
    ) -> BenchmarkResult:
        """
        Run benchmark on PDF file path.
        
        Args:
            pdf_path: Path to PDF file
            library_names: List of library names to use
            
        Returns:
            BenchmarkResult with all extraction results
        """
        # Create temporary document
        pdf_document = PDFDocument(
            filename=pdf_path.name,
            file_path=str(pdf_path),
            size_bytes=pdf_path.stat().st_size if pdf_path.exists() else 0,
        )

        return self.run_benchmark(pdf_document, library_names)
