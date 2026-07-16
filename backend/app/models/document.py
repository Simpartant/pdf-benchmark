"""PDF Document domain model."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class PDFDocument:
    """PDF Document entity."""

    def __init__(
        self,
        filename: str,
        file_path: str,
        size_bytes: int,
        id: Optional[UUID] = None,
        uploaded_at: Optional[datetime] = None,
        status: DocumentStatus = DocumentStatus.UPLOADED,
    ):
        self.id = id or uuid4()
        self.filename = filename
        self.file_path = file_path
        self.size_bytes = size_bytes
        self.uploaded_at = uploaded_at or datetime.now()
        self.status = status

    def mark_processing(self) -> None:
        """Mark document as processing."""
        self.status = DocumentStatus.PROCESSING

    def mark_completed(self) -> None:
        """Mark document as completed."""
        self.status = DocumentStatus.COMPLETED

    def mark_error(self) -> None:
        """Mark document as error."""
        self.status = DocumentStatus.ERROR

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_path": self.file_path,
            "size_bytes": self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat(),
            "status": self.status.value,
        }
