"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# Health schemas
class HealthResponse(BaseModel):
    status: str
    version: str
    pythonVersion: str = Field(alias="python_version")
    uptime: float = Field(description="Uptime in seconds")


# Library schemas
class DependencyInfo(BaseModel):
    name: str
    module: str
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None


class LibraryResponse(BaseModel):
    name: str = Field(description="Library identifier (library_id)")
    displayName: str = Field(alias="display_name", description="Human-readable library name")
    version: str = Field(default="unknown", description="Installed version or 'unknown'")
    status: str = Field(description="available, not_installed, or error")
    installed: bool = Field(description="Whether the library is usable")
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    performanceNotes: Optional[str] = Field(default=None, alias="performance_notes")
    dependencies: List[DependencyInfo] = Field(default_factory=list)
    diagnostics: List[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "serialize_by_alias": True}


class LibrariesResponse(BaseModel):
    libraries: List[LibraryResponse]
    total: int


# Extraction schemas
class ExtractionRequest(BaseModel):
    pdf_path: str = Field(..., description="Path to PDF file")
    libraries: List[str] = Field(..., description="List of library ids to use")


class ExtractionResultResponse(BaseModel):
    """Normalized extraction result response."""
    runId: str
    benchmarkGroupId: str
    library: str
    libraryVersion: str = "unknown"
    originalFilename: str = ""
    status: str
    createdAt: datetime
    markdown: str = ""
    structuredJson: Optional[dict] = None
    metadata: Optional[dict] = None
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    pageCount: int = 0
    tableCount: int = 0
    imageCount: int = 0
    outputFiles: Optional[dict] = None
    fileHash: str = ""
    # Benchmark metrics
    processingTimeSeconds: float = 0.0
    peakMemoryMb: float = 0.0
    averageCpuPercent: float = 0.0
    inputSizeBytes: int = 0
    outputSizeBytes: int = 0
    markdownLength: int = 0
    jsonSizeBytes: int = 0


class BenchmarkResponse(BaseModel):
    """Benchmark result response."""
    id: str
    pdf_filename: str
    pdf_id: str
    file_hash: str = ""
    status: str = "completed"
    extraction_results: List[ExtractionResultResponse]
    total_duration_ms: float
    fastest_library: Optional[str]
    most_efficient_memory: Optional[str]
    most_text_extracted: Optional[str]
    created_at: datetime


# History schemas
class HistoryResponse(BaseModel):
    runId: str
    benchmarkGroupId: str
    filename: str
    createdAt: datetime
    selectedLibrary: str = Field(description="Primary library used")
    status: str = Field(description="success, partial, or failed")
    processingTime: float = Field(description="Processing time in milliseconds")
    peakMemory: float = Field(description="Peak memory usage in MB")
    averageCpu: float = Field(description="Average CPU usage percentage")
    pageCount: int = Field(description="Number of pages extracted")
    outputSize: int = Field(description="Total output size in bytes")


class HistoryListResponse(BaseModel):
    history: List[HistoryResponse]
    total: int


class DeleteResponse(BaseModel):
    success: bool
    message: str