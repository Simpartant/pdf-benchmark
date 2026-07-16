"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# Health schemas
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    pythonVersion: str = Field(alias="python_version")
    uptime: float = Field(description="Uptime in seconds")


# Library schemas
class LibraryResponse(BaseModel):
    """Library information response."""
    name: str = Field(description="Library identifier")
    displayName: str = Field(alias="display_name", description="Human-readable library name")
    installed: bool = Field(description="Whether the library is installed")
    version: Optional[str] = Field(default=None, description="Installed version")
    status: str = Field(description="Library status (available, not_installed, error)")
    description: Optional[str] = Field(default=None, description="Library description")
    capabilities: List[str] = Field(default_factory=list, description="Library capabilities")
    performanceNotes: Optional[str] = Field(default=None, alias="performance_notes", description="Performance notes")
    
    model_config = {"populate_by_name": True}


class LibrariesResponse(BaseModel):
    """List of libraries response."""
    libraries: List[LibraryResponse]
    total: int


# Extraction schemas
class ExtractionRequest(BaseModel):
    """Request to extract text from PDF."""
    pdf_path: str = Field(..., description="Path to PDF file")
    libraries: List[str] = Field(..., description="List of library names to use")


class ExtractionResultResponse(BaseModel):
    """Extraction result response with comprehensive metrics."""
    id: str
    library_name: str
    success: bool
    text_content: str
    execution_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    pages_extracted: int
    char_count: int
    word_count: int
    error_message: Optional[str]
    # Comprehensive output metrics
    output_size_bytes: int = Field(default=0, description="Total size of all output files in bytes")
    images_count: int = Field(default=0, description="Number of images extracted")
    tables_count: int = Field(default=0, description="Number of tables extracted")
    markdown_length: int = Field(default=0, description="Length of markdown output in characters")
    json_size_bytes: int = Field(default=0, description="Size of JSON output in bytes")
    output_directory: Optional[str] = Field(default=None, description="Path to output directory")
    extracted_at: datetime


class BenchmarkResponse(BaseModel):
    """Benchmark result response."""
    id: str
    pdf_filename: str
    pdf_id: str
    extraction_results: List[ExtractionResultResponse]
    total_duration_ms: float
    fastest_library: Optional[str]
    most_efficient_memory: Optional[str]
    most_text_extracted: Optional[str]
    created_at: datetime


# History schemas
class HistoryResponse(BaseModel):
    """History record response."""
    id: str
    pdf_filename: str
    pdf_id: str
    libraries_used: List[str]
    total_duration_ms: float
    success_count: int
    failure_count: int
    benchmark_result_id: str
    created_at: datetime


class HistoryListResponse(BaseModel):
    """List of history records response."""
    history: List[HistoryResponse]
    total: int


class DeleteResponse(BaseModel):
    """Delete operation response."""
    success: bool
    message: str
