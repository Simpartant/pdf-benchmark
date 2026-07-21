"""Benchmark service for running PDF extraction benchmarks."""

from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from app.models.benchmark_result import BenchmarkResult
from app.models.document import PDFDocument
from app.services.extraction_service import ExtractionService
from app.services.history_service import HistoryService
from app.benchmark.result_storage import ResultStorageService
from app.core.config import settings
from loguru import logger


class BenchmarkService:
    """Service for running and managing benchmarks with result storage."""

    def __init__(
        self,
        extraction_service: ExtractionService,
        history_service: HistoryService,
        result_storage: ResultStorageService = None,
    ):
        self.extraction_service = extraction_service
        self.history_service = history_service
        self.result_storage = result_storage or ResultStorageService()

    def run_benchmark(
        self,
        pdf_document: PDFDocument,
        library_names: List[str],
    ) -> BenchmarkResult:
        """Run benchmark on PDF with multiple libraries."""
        logger.info(
            f"Starting benchmark for {pdf_document.filename} "
            f"with libraries: {library_names}"
        )

        pdf_path = Path(pdf_document.file_path)

        # Shared group id so all libraries in this upload are linked.
        benchmark_group_id = uuid4()
        logger.info(f"Generated benchmark_group_id: {benchmark_group_id} for libraries: {library_names}")

        # Base output directory for this benchmark run.
        run_output_dir = (
            Path(settings.results_dir)
            / f"run_{benchmark_group_id.hex[:8]}"
        )
        run_output_dir.mkdir(parents=True, exist_ok=True)

        extraction_results = self.extraction_service.extract_with_multiple_libraries(
            pdf_path=pdf_path,
            library_names=library_names,
            output_dir=run_output_dir,
            benchmark_group_id=benchmark_group_id,
        )

        benchmark_result = BenchmarkResult(
            pdf_filename=pdf_document.filename,
            pdf_id=pdf_document.id,
            extraction_results=extraction_results,
        )
        # Align the benchmark id with the shared group id.
        benchmark_result.id = benchmark_group_id

        benchmark_result.calculate_summary()
        self.history_service.add_history(benchmark_result)

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
        """Run benchmark on PDF file path."""
        pdf_document = PDFDocument(
            filename=pdf_path.name,
            file_path=str(pdf_path),
            size_bytes=pdf_path.stat().st_size if pdf_path.exists() else 0,
        )
        return self.run_benchmark(pdf_document, library_names)