"""History service for managing extraction history."""

from typing import List, Optional
from uuid import UUID
from pathlib import Path
import json

from app.models.history import ExtractionHistory
from app.models.benchmark_result import BenchmarkResult
from app.core.config import settings
from loguru import logger


class HistoryService:
    """Service for managing extraction history records."""

    def __init__(self):
        """Initialize history service."""
        self.history_file = Path(settings.results_dir) / "history.json"
        self._ensure_history_file()

    def _ensure_history_file(self) -> None:
        """Ensure history file exists."""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_history([])

    def _load_history(self) -> List[dict]:
        """Load history from file."""
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    def _save_history(self, history: List[dict]) -> None:
        """Save history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def add_history(self, benchmark_result: BenchmarkResult) -> ExtractionHistory:
        """
        Add a new history record from benchmark result.
        
        Args:
            benchmark_result: BenchmarkResult to convert to history
            
        Returns:
            Created ExtractionHistory record
        """
        # Count successes and failures
        success_count = sum(1 for r in benchmark_result.extraction_results if r.success)
        failure_count = len(benchmark_result.extraction_results) - success_count

        # Get library names
        libraries_used = [r.library_name for r in benchmark_result.extraction_results]

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

        # Save to file
        history_list = self._load_history()
        history_list.append(history_record.to_dict())
        self._save_history(history_list)

        logger.info(f"Added history record: {history_record.id}")
        return history_record

    def get_all_history(self) -> List[ExtractionHistory]:
        """
        Get all history records.
        
        Returns:
            List of ExtractionHistory records
        """
        history_list = self._load_history()
        return [self._dict_to_history(h) for h in history_list]

    def get_history_by_id(self, history_id: UUID) -> Optional[ExtractionHistory]:
        """
        Get history record by ID.
        
        Args:
            history_id: UUID of history record
            
        Returns:
            ExtractionHistory or None if not found
        """
        history_list = self._load_history()
        for h in history_list:
            if h["id"] == str(history_id):
                return self._dict_to_history(h)
        return None

    def delete_history(self, history_id: UUID) -> bool:
        """
        Delete history record by ID.
        
        Args:
            history_id: UUID of history record to delete
            
        Returns:
            True if deleted, False if not found
        """
        history_list = self._load_history()
        initial_length = len(history_list)
        history_list = [h for h in history_list if h["id"] != str(history_id)]
        
        if len(history_list) < initial_length:
            self._save_history(history_list)
            logger.info(f"Deleted history record: {history_id}")
            return True
        
        logger.warning(f"History record not found: {history_id}")
        return False

    def _dict_to_history(self, data: dict) -> ExtractionHistory:
        """Convert dictionary to ExtractionHistory object."""
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
