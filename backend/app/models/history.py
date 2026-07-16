"""Extraction history model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class ExtractionHistory:
    """History record of extraction operations."""

    def __init__(
        self,
        pdf_filename: str,
        pdf_id: UUID,
        libraries_used: list[str],
        total_duration_ms: float,
        success_count: int,
        failure_count: int,
        benchmark_result_id: UUID,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.pdf_filename = pdf_filename
        self.pdf_id = pdf_id
        self.libraries_used = libraries_used
        self.total_duration_ms = total_duration_ms
        self.success_count = success_count
        self.failure_count = failure_count
        self.benchmark_result_id = benchmark_result_id
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "pdf_filename": self.pdf_filename,
            "pdf_id": str(self.pdf_id),
            "libraries_used": self.libraries_used,
            "total_duration_ms": self.total_duration_ms,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "benchmark_result_id": str(self.benchmark_result_id),
            "created_at": self.created_at.isoformat(),
        }
