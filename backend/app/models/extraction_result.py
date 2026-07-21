"""Normalized extraction result domain model.

A single, library-agnostic result produced by any PDF extractor and
enriched with benchmark metrics by the benchmark engine.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4


class ExtractionResult:
    """
    Normalized result of a single PDF extraction.

    Produced in two stages:
    1. The extractor fills the content fields (library, markdown,
       structuredJson, counts, status, error, warnings, outputFiles).
    2. The benchmark engine fills the performance metrics
       (processingTimeSeconds, peakMemoryMb, averageCpuPercent,
       inputSizeBytes, outputSizeBytes, markdownLength, jsonSizeBytes)
       and the run identifiers (runId, benchmarkGroupId, createdAt).
    """

    def __init__(
        self,
        library: str,
        library_version: str = "unknown",
        original_filename: str = "",
        status: str = "success",
        markdown: str = "",
        structured_json: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        error: Optional[str] = None,
        page_count: int = 0,
        table_count: int = 0,
        image_count: int = 0,
        output_files: Optional[Dict[str, Any]] = None,
        # Benchmark metrics (filled by the engine)
        run_id: Optional[UUID] = None,
        benchmark_group_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        processing_time_seconds: float = 0.0,
        peak_memory_mb: float = 0.0,
        average_cpu_percent: float = 0.0,
        input_size_bytes: int = 0,
        output_size_bytes: int = 0,
        markdown_length: int = 0,
        json_size_bytes: int = 0,
        file_hash: str = "",
    ):
        self.run_id = run_id or uuid4()
        self.benchmark_group_id = benchmark_group_id or uuid4()
        self.library = library
        self.library_version = str(library_version) if library_version else "unknown"
        self.original_filename = original_filename
        self.status = status
        self.created_at = created_at or datetime.now()
        self.markdown = markdown
        self.structured_json = structured_json or {}
        self.metadata = metadata or {}
        self.warnings = warnings or []
        self.error = error
        self.page_count = page_count
        self.table_count = table_count
        self.image_count = image_count
        self.output_files = output_files or {}
        # Benchmark metrics
        self.processing_time_seconds = processing_time_seconds
        self.peak_memory_mb = peak_memory_mb
        self.average_cpu_percent = average_cpu_percent
        self.input_size_bytes = input_size_bytes
        self.output_size_bytes = output_size_bytes
        self.markdown_length = markdown_length
        self.json_size_bytes = json_size_bytes
        self.file_hash = file_hash

    # ------------------------------------------------------------------
    # Convenience accessors (kept for backward compatibility with code
    # that referenced the previous model's attributes).
    # ------------------------------------------------------------------
    @property
    def library_name(self) -> str:
        return self.library

    @property
    def success(self) -> bool:
        return self.status == "success"

    @property
    def text_content(self) -> str:
        return self.markdown

    @property
    def error_message(self) -> Optional[str]:
        return self.error

    @property
    def pages_extracted(self) -> int:
        return self.page_count

    @property
    def char_count(self) -> int:
        return len(self.markdown)

    @property
    def word_count(self) -> int:
        words = self.markdown.split()
        return len([w for w in words if w.strip()])

    @property
    def images_count(self) -> int:
        return self.image_count

    @property
    def tables_count(self) -> int:
        return self.table_count

    @property
    def execution_time_ms(self) -> float:
        return self.processing_time_seconds * 1000.0

    @property
    def memory_usage_mb(self) -> float:
        return self.peak_memory_mb

    @property
    def cpu_usage_percent(self) -> float:
        return self.average_cpu_percent

    @property
    def id(self) -> UUID:
        return self.run_id

    def to_dict(self) -> dict:
        """Serialize to the normalized dictionary schema."""
        return {
            "runId": str(self.run_id),
            "benchmarkGroupId": str(self.benchmark_group_id),
            "library": self.library,
            "libraryVersion": str(self.library_version) if self.library_version else "unknown",
            "originalFilename": self.original_filename,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "markdown": self.markdown,
            "structuredJson": self.structured_json,
            "metadata": self.metadata,
            "warnings": self.warnings,
            "error": self.error,
            "pageCount": self.page_count,
            "tableCount": self.table_count,
            "imageCount": self.image_count,
            "outputFiles": self.output_files,
            "fileHash": self.file_hash,
            # Benchmark metrics
            "processingTimeSeconds": self.processing_time_seconds,
            "peakMemoryMb": self.peak_memory_mb,
            "averageCpuPercent": self.average_cpu_percent,
            "inputSizeBytes": self.input_size_bytes,
            "outputSizeBytes": self.output_size_bytes,
            "markdownLength": self.markdown_length,
            "jsonSizeBytes": self.json_size_bytes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractionResult":
        """Reconstruct an ExtractionResult from a normalized dict."""
        from uuid import UUID as _UUID

        def _uuid(value, default=None):
            if value is None:
                return default or uuid4()
            if isinstance(value, _UUID):
                return value
            try:
                return _UUID(str(value))
            except Exception:
                return default or uuid4()

        def _dt(value):
            if value is None:
                return datetime.now()
            if isinstance(value, datetime):
                return value
            try:
                return datetime.fromisoformat(str(value))
            except Exception:
                return datetime.now()

        return cls(
            library=data.get("library", data.get("library_name", "unknown")),
            library_version=str(data.get("libraryVersion", "unknown")) if data.get("libraryVersion") else "unknown",
            original_filename=data.get("originalFilename", ""),
            status=data.get("status", "success" if data.get("success", True) else "failed"),
            markdown=data.get("markdown", data.get("text_content", "")),
            structured_json=data.get("structuredJson", data.get("structured_json", {})),
            metadata=data.get("metadata", {}),
            warnings=data.get("warnings", []),
            error=data.get("error", data.get("error_message")),
            page_count=data.get("pageCount", data.get("pages_extracted", 0)),
            table_count=data.get("tableCount", data.get("tables_count", 0)),
            image_count=data.get("imageCount", data.get("images_count", 0)),
            output_files=data.get("outputFiles", data.get("output_files", {})),
            run_id=_uuid(data.get("runId", data.get("id"))),
            benchmark_group_id=_uuid(data.get("benchmarkGroupId")),
            created_at=_dt(data.get("createdAt", data.get("extracted_at"))),
            processing_time_seconds=data.get(
                "processingTimeSeconds",
                (data.get("execution_time_ms", 0) or 0) / 1000.0,
            ),
            peak_memory_mb=data.get("peakMemoryMb", data.get("memory_usage_mb", 0)),
            average_cpu_percent=data.get(
                "averageCpuPercent", data.get("cpu_usage_percent", 0)
            ),
            input_size_bytes=data.get("inputSizeBytes", 0),
            output_size_bytes=data.get(
                "outputSizeBytes", data.get("output_size_bytes", 0)
            ),
            markdown_length=data.get("markdownLength", data.get("markdown_length", 0)),
            json_size_bytes=data.get("jsonSizeBytes", data.get("json_size_bytes", 0)),
            file_hash=data.get("fileHash", ""),
        )