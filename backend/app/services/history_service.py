"""History service for managing extraction history."""

from typing import List, Optional
from uuid import UUID
from pathlib import Path
import json
from datetime import datetime

from app.models.history import ExtractionHistory
from app.models.benchmark_result import BenchmarkResult
from app.core.config import settings
from loguru import logger


class HistoryService:
    """Service for managing extraction history records."""

    def __init__(self):
        """Initialize history service."""
        self.results_dir = Path(settings.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _scan_result_directories(self) -> List[Path]:
        """Scan results directory for valid result directories."""
        if not self.results_dir.exists():
            return []

        result_dirs = []
        try:
            for item in self.results_dir.iterdir():
                if item.is_dir() and item.name.startswith("20"):
                    if (item / "benchmark.json").exists() or (item / "metadata.json").exists():
                        result_dirs.append(item)
        except Exception as e:
            logger.error(f"Error scanning results directory: {e}")

        result_dirs.sort(key=lambda p: p.name, reverse=True)
        return result_dirs

    def _load_history_from_dir(self, result_dir: Path) -> Optional[ExtractionHistory]:
        """Load history record from a result directory (normalized schema)."""
        metadata_file = result_dir / "metadata.json"
        benchmark_file = result_dir / "benchmark.json"

        if not metadata_file.exists() and not benchmark_file.exists():
            return None

        try:
            benchmark_data = {}
            if benchmark_file.exists():
                with open(benchmark_file, "r") as f:
                    benchmark_data = json.load(f)

            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)

            benchmark_id = benchmark_data.get("benchmark_id") or metadata.get("benchmark_id")
            if not benchmark_id:
                return None

            pdf_filename = benchmark_data.get("pdf_filename") or metadata.get("pdf_filename", "unknown.pdf")
            pdf_id = benchmark_data.get("pdf_id") or metadata.get("pdf_id", str(UUID(int=0)))
            created_at_str = benchmark_data.get("created_at") or metadata.get("created_at")

            created_at = datetime.now()
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except Exception:
                    pass

            extraction_results = benchmark_data.get("extraction_results", [])
            libraries_used = [
                r.get("library") or r.get("library_name")
                for r in extraction_results
                if (r.get("library") or r.get("library_name"))
            ]

            success_count = sum(1 for r in extraction_results if r.get("status") == "success")
            failure_count = len(extraction_results) - success_count

            total_duration_ms = benchmark_data.get("total_duration_ms", 0)

            return ExtractionHistory(
                id=UUID(benchmark_id),
                pdf_filename=pdf_filename,
                pdf_id=UUID(pdf_id),
                libraries_used=libraries_used,
                total_duration_ms=total_duration_ms,
                success_count=success_count,
                failure_count=failure_count,
                benchmark_result_id=UUID(benchmark_id),
                created_at=created_at,
            )

        except Exception as e:
            logger.error(f"Failed to load history from {result_dir}: {e}")
            return None

    def _load_history(self) -> List[dict]:
        history_file = self.results_dir / "history.json"
        try:
            if history_file.exists():
                with open(history_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
        return []

    def _save_history(self, history: List[dict]) -> None:
        history_file = self.results_dir / "history.json"
        try:
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_history(self, benchmark_result: BenchmarkResult) -> ExtractionHistory:
        """Add a new history record from benchmark result."""
        success_count = sum(1 for r in benchmark_result.extraction_results if r.success)
        failure_count = len(benchmark_result.extraction_results) - success_count

        libraries_used = [r.library for r in benchmark_result.extraction_results]

        history_record = ExtractionHistory(
            pdf_filename=benchmark_result.pdf_filename,
            pdf_id=benchmark_result.pdf_id,
            libraries_used=libraries_used,
            total_duration_ms=benchmark_result.total_duration_ms,
            success_count=success_count,
            failure_count=failure_count,
            benchmark_result_id=benchmark_result.id,
            created_at=benchmark_result.created_at,
        )

        history_list = self._load_history()
        history_list.append(history_record.to_dict())
        self._save_history(history_list)

        logger.info(f"Added history record: {history_record.id}")
        return history_record

    def get_all_history(self) -> List[ExtractionHistory]:
        result_dirs = self._scan_result_directories()
        history_records = []
        for result_dir in result_dirs:
            try:
                record = self._load_history_from_dir(result_dir)
                if record:
                    history_records.append(record)
            except Exception as e:
                logger.warning(f"Failed to load history from {result_dir}: {e}")
                continue
        history_records.sort(key=lambda h: h.created_at, reverse=True)
        return history_records

    def get_history_by_id(self, history_id: UUID) -> Optional[ExtractionHistory]:
        result_dirs = self._scan_result_directories()
        for result_dir in result_dirs:
            try:
                record = self._load_history_from_dir(result_dir)
                if record and record.id == history_id:
                    return record
            except Exception:
                continue
        return None

    def get_history_by_benchmark_group(
        self, benchmark_group_id: UUID
    ) -> List[ExtractionHistory]:
        """Get all history records for a given benchmark group ID."""
        result_dirs = self._scan_result_directories()
        history_records = []
        for result_dir in result_dirs:
            try:
                benchmark_file = result_dir / "benchmark.json"
                if not benchmark_file.exists():
                    continue
                with open(benchmark_file, "r") as f:
                    benchmark_data = json.load(f)
                if benchmark_data.get("benchmarkGroupId") == str(benchmark_group_id):
                    record = self._load_history_from_dir(result_dir)
                    if record:
                        history_records.append(record)
            except Exception as e:
                logger.debug(f"Could not check benchmark group in {result_dir}: {e}")
                continue
        return history_records

    def delete_history(self, history_id: UUID) -> bool:
        result_dirs = self._scan_result_directories()
        for result_dir in result_dirs:
            try:
                record = self._load_history_from_dir(result_dir)
                if record and record.id == history_id:
                    import shutil
                    shutil.rmtree(result_dir)
                    logger.info(f"Deleted result directory: {result_dir}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to delete {result_dir}: {e}")
                continue
        logger.warning(f"History record not found: {history_id}")
        return False

    def _dict_to_history(self, data: dict) -> ExtractionHistory:
        from datetime import datetime

        return ExtractionHistory(
            id=UUID(data["id"]),
            pdf_filename=data["pdf_filename"],
            pdf_id=UUID(data["pdf_id"]),
            libraries_used=data["libraries_used"],
            total_duration_ms=data["total_duration_ms"],
            success_count=data["success_count"],
            failure_count=data["failure_count"],
            benchmark_result_id=UUID(data["benchmark_result_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )