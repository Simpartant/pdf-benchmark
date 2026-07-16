"""Library information model."""

from typing import Optional, List
from enum import Enum


class LibraryStatus(str, Enum):
    """Library availability status."""
    AVAILABLE = "available"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"


class Library:
    """PDF extraction library information."""

    def __init__(
        self,
        name: str,
        display_name: str,
        version: Optional[str] = None,
        description: Optional[str] = None,
        status: LibraryStatus = LibraryStatus.NOT_INSTALLED,
        capabilities: Optional[List[str]] = None,
        performance_notes: Optional[str] = None,
    ):
        self.name = name
        self.display_name = display_name
        self.version = version
        self.description = description
        self.status = status
        self.capabilities = capabilities or []
        self.performance_notes = performance_notes

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "performance_notes": self.performance_notes,
        }
