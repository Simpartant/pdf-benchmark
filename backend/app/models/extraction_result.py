"""Extraction result domain model."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class ExtractionResult:
    """Result of PDF extraction operation with comprehensive metrics."""

    def __init__(
        self,
        library_name: str,
        success: bool,
        text_content: str = "",
        execution_time_ms: float = 0.0,
        memory_usage_mb: float = 0.0,
        cpu_usage_percent: float = 0.0,
        pages_extracted: int = 0,
        char_count: int = 0,
        word_count: int = 0,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # New comprehensive metrics
        output_size_bytes: int = 0,
        images_count: int = 0,
        tables_count: int = 0,
        markdown_length: int = 0,
        json_size_bytes: int = 0,
        output_directory: Optional[str] = None,
        id: Optional[UUID] = None,
        extracted_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.library_name = library_name
        self.success = success
        self.text_content = text_content
        self.execution_time_ms = execution_time_ms
        self.memory_usage_mb = memory_usage_mb
        self.cpu_usage_percent = cpu_usage_percent
        self.pages_extracted = pages_extracted
        self.char_count = char_count
        self.word_count = word_count
        self.error_message = error_message
        self.metadata = metadata or {}
        # New comprehensive metrics
        self.output_size_bytes = output_size_bytes
        self.images_count = images_count
        self.tables_count = tables_count
        self.markdown_length = markdown_length
        self.json_size_bytes = json_size_bytes
        self.output_directory = output_directory
        self.extracted_at = extracted_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary with all metrics."""
        return {
            "id": str(self.id),
            "library_name": self.library_name,
            "success": self.success,
            "text_content": self.text_content,
            "execution_time_ms": self.execution_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "pages_extracted": self.pages_extracted,
            "char_count": self.char_count,
            "word_count": self.word_count,
            "error_message": self.error_message,
            "metadata": self.metadata,
            # Comprehensive metrics
            "output_size_bytes": self.output_size_bytes,
            "images_count": self.images_count,
            "tables_count": self.tables_count,
            "markdown_length": self.markdown_length,
            "json_size_bytes": self.json_size_bytes,
            "output_directory": self.output_directory,
            "extracted_at": self.extracted_at.isoformat(),
        }
