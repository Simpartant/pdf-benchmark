"""Extraction service for coordinating PDF extractions."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.extractors.base_extractor import BaseExtractor
from app.extractors.registry import extractor_registry
from app.models.extraction_result import ExtractionResult
from app.models.document import PDFDocument
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.services.report_service import ReportService
from loguru import logger


class ExtractionService:
    """Service for managing PDF extraction operations with benchmarking."""

    def __init__(self, benchmark_engine: Optional[BenchmarkEngine] = None):
        """
        Initialize extraction service.

        Extractors are resolved lazily through the registry, so no
        hardcoded mapping is kept here.

        Args:
            benchmark_engine: Optional BenchmarkEngine for performance monitoring
        """
        self.benchmark_engine = benchmark_engine or BenchmarkEngine()
        self.report_service = ReportService()

    def get_extractor(self, library_name: str) -> Optional[BaseExtractor]:
        """
        Get extractor by library id from the registry.

        Args:
            library_name: Id of the extraction library

        Returns:
            BaseExtractor instance or None if not registered
        """
        return extractor_registry.get(library_name)

    def extract_with_library(
        self,
        pdf_path: Path,
        library_name: str,
        output_dir: Path,
        options: Optional[dict] = None,
        benchmark_group_id: Optional[UUID] = None,
    ) -> ExtractionResult:
        """
        Extract text from PDF using the specified library with benchmarking.

        Args:
            pdf_path: Path to PDF file
            library_name: Id of library to use
            output_dir: Directory where extraction artifacts are written
            options: Optional extractor-specific options
            benchmark_group_id: Optional shared group ID for multi-library runs

        Returns:
            ExtractionResult enriched with performance metrics
        """
        extractor = self.get_extractor(library_name)
        if extractor is None:
            logger.error(f"Unknown extraction library: {library_name}")
            return ExtractionResult(
                library=library_name,
                original_filename=pdf_path.name if pdf_path else "",
                status="failed",
                error=f"Unknown extraction library: {library_name}",
            )

        try:
            logger.info(f"Starting benchmarked extraction with {library_name}")
            result = self.benchmark_engine.run_extraction(
                extractor=extractor,
                pdf_path=pdf_path,
                output_dir=output_dir,
                options=options,
                benchmark_group_id=benchmark_group_id,
            )
            logger.info(
                f"Extraction completed: {library_name}, "
                f"status={result.status}, "
                f"chars={len(result.markdown)}, "
                f"time={result.processing_time_seconds:.2f}s"
            )
            return result
        except Exception as e:
            logger.exception(f"Extraction failed with {library_name}: {str(e)}")
            return ExtractionResult(
                library=library_name,
                original_filename=pdf_path.name if pdf_path else "",
                status="failed",
                error=str(e),
            )

    def extract_with_multiple_libraries(
        self,
        pdf_path: Path,
        library_names: List[str],
        output_dir: Path,
        options: Optional[dict] = None,
        benchmark_group_id: Optional[UUID] = None,
    ) -> List[ExtractionResult]:
        """
        Extract text using multiple libraries.

        Args:
            pdf_path: Path to PDF file
            library_names: List of library ids to use
            output_dir: Base directory; each library gets its own subfolder
            options: Optional extractor-specific options
            benchmark_group_id: Optional shared group ID for multi-library runs

        Returns:
            List of ExtractionResult objects
        """
        results = []
        for library_name in library_names:
            library_output_dir = Path(output_dir) / library_name
            result = self.extract_with_library(
                pdf_path=pdf_path,
                library_name=library_name,
                output_dir=library_output_dir,
                options=options,
                benchmark_group_id=benchmark_group_id,
            )
            results.append(result)
        return results

    def get_available_extractors(self) -> List[str]:
        """Return all registered extractor ids."""
        return extractor_registry.list_ids()

    def run_benchmark_with_report(
        self,
        pdf_path: Path,
        library_names: List[str],
        output_dir: Path,
    ) -> tuple[List[ExtractionResult], Path]:
        """
        Run benchmark extractions and generate a comprehensive report.

        Args:
            pdf_path: Path to PDF file
            library_names: List of library ids to benchmark
            output_dir: Directory to save results and report

        Returns:
            Tuple of (extraction results, report path)
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        results_dir = Path(output_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting benchmark with report for {len(library_names)} libraries")
        results = self.extract_with_multiple_libraries(
            pdf_path, library_names, results_dir
        )

        pdf_info = {
            "name": pdf_path.name,
            "size": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "pages": 0,
        }

        benchmark_results = {}
        for result in results:
            benchmark_results[result.library] = {
                "status": result.status,
                "processingTimeSeconds": result.processing_time_seconds,
                "peakMemoryMb": result.peak_memory_mb,
                "averageCpuPercent": result.average_cpu_percent,
                "outputs": {
                    "markdown_size": result.markdown_length,
                    "json_size": result.json_size_bytes,
                    "images_count": result.image_count,
                    "tables_count": result.table_count,
                },
                "error": result.error,
            }

        report_path = self.report_service.generate_report(
            benchmark_results=benchmark_results,
            pdf_info=pdf_info,
            output_dir=results_dir,
        )

        logger.info(f"Benchmark report generated: {report_path}")
        return results, report_path