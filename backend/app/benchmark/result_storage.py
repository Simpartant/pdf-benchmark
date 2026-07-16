"""Result storage service for saving benchmark results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from loguru import logger

from app.models.benchmark_result import BenchmarkResult
from app.models.extraction_result import ExtractionResult
from app.core.config import settings


class ResultStorageService:
    """
    Service for storing benchmark results to disk.
    
    Stores results in timestamped directories with JSON files.
    """

    def __init__(self):
        """Initialize result storage service."""
        self.results_dir = Path(settings.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def store_benchmark_result(
        self,
        benchmark_result: BenchmarkResult,
    ) -> Path:
        """
        Store benchmark result to disk.
        
        Creates directory: results/{timestamp}/
        Files:
        - benchmark.json: Full benchmark results
        - metadata.json: Metadata and summary
        
        Args:
            benchmark_result: BenchmarkResult to store
            
        Returns:
            Path to result directory
        """
        # Create timestamped directory
        timestamp = benchmark_result.created_at.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        result_dir = self.results_dir / timestamp
        result_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storing benchmark result to {result_dir}")
        
        # Store benchmark.json
        benchmark_file = result_dir / "benchmark.json"
        benchmark_data = self._prepare_benchmark_data(benchmark_result)
        self._write_json(benchmark_file, benchmark_data)
        
        # Store metadata.json
        metadata_file = result_dir / "metadata.json"
        metadata = self._prepare_metadata(benchmark_result)
        self._write_json(metadata_file, metadata)
        
        # Store individual extraction results
        for idx, extraction_result in enumerate(benchmark_result.extraction_results):
            result_file = result_dir / f"extraction_{extraction_result.library_name}.json"
            extraction_data = extraction_result.to_dict()
            self._write_json(result_file, extraction_data)
        
        logger.info(f"Benchmark result stored successfully: {result_dir}")
        
        return result_dir

    def _prepare_benchmark_data(self, benchmark_result: BenchmarkResult) -> Dict[str, Any]:
        """
        Prepare complete benchmark data for storage.
        
        Args:
            benchmark_result: BenchmarkResult to convert
            
        Returns:
            Dictionary with benchmark data
        """
        return {
            "benchmark_id": str(benchmark_result.id),
            "pdf_filename": benchmark_result.pdf_filename,
            "pdf_id": str(benchmark_result.pdf_id),
            "created_at": benchmark_result.created_at.isoformat(),
            "total_duration_ms": benchmark_result.total_duration_ms,
            "summary": {
                "fastest_library": benchmark_result.fastest_library,
                "most_efficient_memory": benchmark_result.most_efficient_memory,
                "most_text_extracted": benchmark_result.most_text_extracted,
            },
            "extraction_results": [
                {
                    "library_name": result.library_name,
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                    "memory_usage_mb": result.memory_usage_mb,
                    "cpu_usage_percent": result.cpu_usage_percent,
                    "pages_extracted": result.pages_extracted,
                    "char_count": result.char_count,
                    "word_count": result.word_count,
                    "error_message": result.error_message,
                    # Comprehensive output metrics
                    "output_size_bytes": result.output_size_bytes,
                    "images_count": result.images_count,
                    "tables_count": result.tables_count,
                    "markdown_length": result.markdown_length,
                    "json_size_bytes": result.json_size_bytes,
                    "output_directory": result.output_directory,
                    "extracted_at": result.extracted_at.isoformat(),
                }
                for result in benchmark_result.extraction_results
            ],
            "metadata": benchmark_result.metadata,
        }

    def _prepare_metadata(self, benchmark_result: BenchmarkResult) -> Dict[str, Any]:
        """
        Prepare metadata summary.
        
        Args:
            benchmark_result: BenchmarkResult to summarize
            
        Returns:
            Dictionary with metadata
        """
        # Calculate statistics
        successful_results = [
            r for r in benchmark_result.extraction_results if r.success
        ]
        failed_results = [
            r for r in benchmark_result.extraction_results if not r.success
        ]
        
        metadata = {
            "benchmark_id": str(benchmark_result.id),
            "pdf_filename": benchmark_result.pdf_filename,
            "created_at": benchmark_result.created_at.isoformat(),
            "summary": {
                "total_libraries_tested": len(benchmark_result.extraction_results),
                "successful_extractions": len(successful_results),
                "failed_extractions": len(failed_results),
                "total_duration_ms": benchmark_result.total_duration_ms,
                "fastest_library": benchmark_result.fastest_library,
                "most_efficient_memory": benchmark_result.most_efficient_memory,
                "most_text_extracted": benchmark_result.most_text_extracted,
            },
            "performance_comparison": {
                "execution_times": {
                    result.library_name: result.execution_time_ms
                    for result in benchmark_result.extraction_results
                },
                "memory_usage": {
                    result.library_name: result.memory_usage_mb
                    for result in benchmark_result.extraction_results
                },
                "cpu_usage": {
                    result.library_name: result.cpu_usage_percent
                    for result in benchmark_result.extraction_results
                },
                "output_sizes": {
                    result.library_name: result.output_size_bytes
                    for result in benchmark_result.extraction_results
                },
                "images_extracted": {
                    result.library_name: result.images_count
                    for result in benchmark_result.extraction_results
                },
                "tables_extracted": {
                    result.library_name: result.tables_count
                    for result in benchmark_result.extraction_results
                },
            },
            "libraries_tested": [
                {
                    "name": result.library_name,
                    "success": result.success,
                    "error": result.error_message,
                }
                for result in benchmark_result.extraction_results
            ],
        }
        
        # Add best performers for new metrics
        if successful_results:
            # Most images extracted
            most_images = max(successful_results, key=lambda r: r.images_count, default=None)
            if most_images and most_images.images_count > 0:
                metadata["summary"]["most_images_extracted"] = most_images.library_name
            
            # Most tables extracted
            most_tables = max(successful_results, key=lambda r: r.tables_count, default=None)
            if most_tables and most_tables.tables_count > 0:
                metadata["summary"]["most_tables_extracted"] = most_tables.library_name
            
            # Smallest output size (most efficient storage)
            smallest_output = min(
                [r for r in successful_results if r.output_size_bytes > 0],
                key=lambda r: r.output_size_bytes,
                default=None
            )
            if smallest_output:
                metadata["summary"]["most_efficient_storage"] = smallest_output.library_name
        
        return metadata

    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """
        Write JSON data to file.
        
        Args:
            file_path: Path to write to
            data: Data to write
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Wrote JSON to {file_path}")
        except Exception as e:
            logger.error(f"Failed to write JSON to {file_path}: {e}")
            raise

    def load_benchmark_result(self, result_dir: Path) -> Dict[str, Any]:
        """
        Load benchmark result from directory.
        
        Args:
            result_dir: Path to result directory
            
        Returns:
            Dictionary with benchmark data
        """
        benchmark_file = result_dir / "benchmark.json"
        if not benchmark_file.exists():
            raise FileNotFoundError(f"Benchmark file not found: {benchmark_file}")
        
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_stored_results(self) -> List[Path]:
        """
        List all stored result directories.
        
        Returns:
            List of result directory paths
        """
        if not self.results_dir.exists():
            return []
        
        # Find directories with timestamp pattern
        result_dirs = [
            d for d in self.results_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        # Sort by creation time (newest first)
        result_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        
        return result_dirs
