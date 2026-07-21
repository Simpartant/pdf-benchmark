"""Benchmark engine for running and measuring PDF extractions."""

import hashlib
import time
import json
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from uuid import uuid4, UUID

from loguru import logger

from app.benchmark.performance_monitor import PerformanceMonitor, PerformanceMetrics
from app.models.extraction_result import ExtractionResult
from app.utils.text_utils import count_words, count_characters
from app.core.config import settings
from app.extractors.base_extractor import BaseExtractor


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


class BenchmarkEngine:
    """
    Engine for running benchmarked extractions with performance monitoring.

    Wraps an extractor's ``extract`` method and measures:
    - Execution time
    - Peak memory usage
    - Average CPU usage
    and then enriches the returned :class:`ExtractionResult` with those
    metrics plus run identifiers.
    """

    def __init__(self, sampling_interval_ms: float = 50):
        self.sampling_interval_ms = sampling_interval_ms

    def run_extraction(
        self,
        extractor: BaseExtractor,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
        benchmark_group_id: Optional[UUID] = None,
    ) -> ExtractionResult:
        """
        Run an extractor with performance monitoring and enrich the result.

        Args:
            extractor: The extractor instance to run.
            pdf_path: Path to the PDF file.
            output_dir: Directory where extraction artifacts are written.
            options: Optional extractor-specific options.
            benchmark_group_id: Shared group id for this benchmark run.

        Returns:
            ExtractionResult enriched with performance metrics and ids.
        """
        logger.info(f"Starting benchmarked extraction with {extractor.library_id}")

        monitor = PerformanceMonitor(sampling_interval_ms=self.sampling_interval_ms)

        # Calculate file hash for the immutable source PDF
        file_hash = calculate_file_hash(pdf_path) if pdf_path and pdf_path.exists() else ""

        result: Optional[ExtractionResult] = None
        start_time = time.time()
        try:
            monitor.start()

            result = extractor.extract(
                pdf_path=pdf_path,
                output_dir=output_dir,
                options=options,
            )

            end_time = time.time()
            metrics = monitor.stop()
            elapsed_seconds = end_time - start_time
            logger.info(
                f"Extraction completed: {extractor.library_id}, "
                f"time={metrics.elapsed_time_ms:.2f}ms"
            )
        except Exception as e:
            metrics = monitor.stop()
            elapsed_seconds = time.time() - start_time
            logger.exception(f"Extraction failed with {extractor.library_id}: {e}")
            result = ExtractionResult(
                library=extractor.library_id,
                original_filename=pdf_path.name if pdf_path else "",
                status="failed",
                error=str(e),
            )

        # Enrich with performance metrics and run identifiers.
        result.benchmark_group_id = benchmark_group_id or uuid4()
        result.run_id = uuid4()
        result.created_at = datetime.now()
        result.processing_time_seconds = elapsed_seconds
        result.peak_memory_mb = metrics.peak_memory_mb
        result.average_cpu_percent = metrics.average_cpu_percent
        result.input_size_bytes = (
            pdf_path.stat().st_size if pdf_path and pdf_path.exists() else 0
        )
        result.file_hash = file_hash
        result.markdown_length = len(result.markdown or "")
        result.json_size_bytes = self._collect_json_size(output_dir)
        result.output_size_bytes = self._collect_output_size(output_dir)

        return result

    def _collect_json_size(self, output_dir: Path) -> int:
        try:
            json_file = Path(output_dir) / "document.json"
            if not json_file.exists():
                json_file = Path(output_dir) / "elements.json"
            if not json_file.exists():
                json_file = Path(output_dir) / "documents.json"
            if not json_file.exists():
                json_file = Path(output_dir) / "content.json"
            if json_file.exists():
                return json_file.stat().st_size
        except Exception:
            pass
        return 0

    def _collect_output_size(self, output_dir: Path) -> int:
        try:
            total = 0
            for file in Path(output_dir).rglob("*"):
                if file.is_file():
                    total += file.stat().st_size
            return total
        except Exception:
            return 0