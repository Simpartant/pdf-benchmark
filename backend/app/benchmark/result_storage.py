"""Result storage service for saving benchmark results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID

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
        timestamp = benchmark_result.created_at.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        result_dir = self.results_dir / timestamp
        result_dir.mkdir(parents=True, exist_ok=True)

        # Get benchmark_group_id from first result
        benchmark_group_id = None
        if benchmark_result.extraction_results:
            benchmark_group_id = benchmark_result.extraction_results[0].benchmark_group_id

        logger.info(f"Storing benchmark result to {result_dir}, group_id: {benchmark_group_id}, storage_id: {id(self)}")
        
        # Log all available group IDs
        all_results = self.list_stored_results()
        available_ids = []
        for r in all_results:
            bf = r / "benchmark.json"
            if bf.exists():
                try:
                    import json
                    with open(bf) as f:
                        data = json.load(f)
                        available_ids.append(data.get("benchmarkGroupId"))
                except:
                    pass
        logger.info(f"Available group IDs before save: {available_ids}")

        benchmark_file = result_dir / "benchmark.json"
        benchmark_data = self._prepare_benchmark_data(benchmark_result)
        self._write_json(benchmark_file, benchmark_data)

        metadata_file = result_dir / "metadata.json"
        metadata = self._prepare_metadata(benchmark_result)
        self._write_json(metadata_file, metadata)

        for idx, extraction_result in enumerate(benchmark_result.extraction_results):
            result_file = result_dir / f"extraction_{extraction_result.library}.json"
            extraction_data = extraction_result.to_dict()
            self._write_json(result_file, extraction_data)

        logger.info(f"Benchmark result stored successfully: {result_dir}")
        return result_dir

    def _prepare_benchmark_data(self, benchmark_result: BenchmarkResult) -> Dict[str, Any]:
        """
        Prepare complete benchmark data for storage (normalized schema).
        """
        # Get file hash from first result
        file_hash = ""
        benchmark_group_id = None
        if benchmark_result.extraction_results:
            file_hash = benchmark_result.extraction_results[0].file_hash
            benchmark_group_id = benchmark_result.extraction_results[0].benchmark_group_id

        return {
            "benchmark_id": str(benchmark_result.id),
            "benchmarkGroupId": str(benchmark_group_id) if benchmark_group_id else str(benchmark_result.id),
            "pdf_filename": benchmark_result.pdf_filename,
            "pdf_id": str(benchmark_result.pdf_id),
            "file_hash": file_hash,
            "created_at": benchmark_result.created_at.isoformat(),
            "total_duration_ms": benchmark_result.total_duration_ms,
            "summary": {
                "fastest_library": benchmark_result.fastest_library,
                "most_efficient_memory": benchmark_result.most_efficient_memory,
                "most_text_extracted": benchmark_result.most_text_extracted,
            },
            "extraction_results": [
                result.to_dict() for result in benchmark_result.extraction_results
            ],
            "metadata": benchmark_result.metadata,
        }

    def _prepare_metadata(self, benchmark_result: BenchmarkResult) -> Dict[str, Any]:
        """Prepare metadata summary (normalized schema)."""
        successful_results = [
            r for r in benchmark_result.extraction_results if r.success
        ]
        failed_results = [
            r for r in benchmark_result.extraction_results if not r.success
        ]

        # Get file hash and benchmark_group_id from first result
        file_hash = ""
        benchmark_group_id = None
        if benchmark_result.extraction_results:
            file_hash = benchmark_result.extraction_results[0].file_hash
            benchmark_group_id = benchmark_result.extraction_results[0].benchmark_group_id

        metadata = {
            "benchmark_id": str(benchmark_result.id),
            "benchmarkGroupId": str(benchmark_group_id) if benchmark_group_id else str(benchmark_result.id),
            "pdf_filename": benchmark_result.pdf_filename,
            "file_hash": file_hash,
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
                "processing_time_seconds": {
                    result.library: result.processing_time_seconds
                    for result in benchmark_result.extraction_results
                },
                "peak_memory_mb": {
                    result.library: result.peak_memory_mb
                    for result in benchmark_result.extraction_results
                },
                "average_cpu_percent": {
                    result.library: result.average_cpu_percent
                    for result in benchmark_result.extraction_results
                },
                "output_size_bytes": {
                    result.library: result.output_size_bytes
                    for result in benchmark_result.extraction_results
                },
                "image_count": {
                    result.library: result.image_count
                    for result in benchmark_result.extraction_results
                },
                "table_count": {
                    result.library: result.table_count
                    for result in benchmark_result.extraction_results
                },
            },
            "libraries_tested": [
                {
                    "name": result.library,
                    "success": result.success,
                    "error": result.error,
                }
                for result in benchmark_result.extraction_results
            ],
        }
        return metadata

    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Wrote JSON to {file_path}")
        except Exception as e:
            logger.error(f"Failed to write JSON to {file_path}: {e}")
            raise

    def load_benchmark_result(self, result_dir: Path) -> Dict[str, Any]:
        benchmark_file = result_dir / "benchmark.json"
        if not benchmark_file.exists():
            raise FileNotFoundError(f"Benchmark file not found: {benchmark_file}")
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_by_benchmark_id(self, benchmark_id: UUID) -> dict:
        result_dirs = self.list_stored_results()
        for result_dir in result_dirs:
            benchmark_file = result_dir / "benchmark.json"
            if not benchmark_file.exists():
                continue
            try:
                with open(benchmark_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("benchmark_id") == str(benchmark_id):
                    return data
            except Exception:
                continue
        raise FileNotFoundError(f"Benchmark result not found for ID: {benchmark_id}")

    def load_by_benchmark_group_id(self, benchmark_group_id: UUID) -> dict:
        """Load benchmark result by benchmark group ID."""
        result_dirs = self.list_stored_results()
        for result_dir in result_dirs:
            benchmark_file = result_dir / "benchmark.json"
            if not benchmark_file.exists():
                continue
            try:
                with open(benchmark_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("benchmarkGroupId") == str(benchmark_group_id):
                    return data
            except Exception:
                continue
        raise FileNotFoundError(f"Benchmark result not found for group ID: {benchmark_group_id}")

    def list_stored_results(self) -> List[Path]:
        if not self.results_dir.exists():
            return []
        result_dirs = [
            d for d in self.results_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        result_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        return result_dirs