"""Benchmark result domain model."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from .extraction_result import ExtractionResult


class BenchmarkResult:
    """Result of benchmarking multiple extraction libraries."""

    def __init__(
        self,
        pdf_filename: str,
        pdf_id: UUID,
        extraction_results: List[ExtractionResult],
        total_duration_ms: float = 0.0,
        fastest_library: Optional[str] = None,
        most_efficient_memory: Optional[str] = None,
        most_text_extracted: Optional[str] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id or uuid4()
        self.pdf_filename = pdf_filename
        self.pdf_id = pdf_id
        self.extraction_results = extraction_results
        self.total_duration_ms = total_duration_ms
        self.fastest_library = fastest_library
        self.most_efficient_memory = most_efficient_memory
        self.most_text_extracted = most_text_extracted
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}

    def calculate_summary(self) -> None:
        """Calculate summary statistics."""
        if not self.extraction_results:
            return

        # Filter successful results
        successful_results = [r for r in self.extraction_results if r.success]
        
        if successful_results:
            # Find fastest
            fastest = min(successful_results, key=lambda r: r.execution_time_ms)
            self.fastest_library = fastest.library_name

            # Find most memory efficient
            most_efficient = min(successful_results, key=lambda r: r.memory_usage_mb)
            self.most_efficient_memory = most_efficient.library_name

            # Find most text extracted
            most_text = max(successful_results, key=lambda r: r.char_count)
            self.most_text_extracted = most_text.library_name

            # Calculate total duration
            self.total_duration_ms = sum(r.execution_time_ms for r in self.extraction_results)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "pdf_filename": self.pdf_filename,
            "pdf_id": str(self.pdf_id),
            "extraction_results": [r.to_dict() for r in self.extraction_results],
            "total_duration_ms": self.total_duration_ms,
            "fastest_library": self.fastest_library,
            "most_efficient_memory": self.most_efficient_memory,
            "most_text_extracted": self.most_text_extracted,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
