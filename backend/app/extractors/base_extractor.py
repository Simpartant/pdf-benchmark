"""Base extractor abstract class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.models.extraction_result import ExtractionResult


class BaseExtractor(ABC):
    """
    Abstract base class for PDF extractors.
    
    All extraction implementations must inherit from this class
    and implement the extract method.
    """

    def __init__(self, library_name: str):
        """
        Initialize the extractor.
        
        Args:
            library_name: Name of the extraction library
        """
        self.library_name = library_name

    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract text and metadata from a PDF file.
        
        This method is deprecated. Use extract_text() for benchmarked extractions.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            ExtractionResult: Result containing extracted text and metrics
            
        Raises:
            FileNotFoundError: If PDF file does not exist
            Exception: For extraction errors
        """
        pass

    @abstractmethod
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract only text from a PDF file.
        
        This method is used by the benchmark engine for performance monitoring.
        Should return only the extracted text string.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileNotFoundError: If PDF file does not exist
            Exception: For extraction errors
        """
        pass

    def validate_pdf(self, pdf_path: Path) -> None:
        """
        Validate that the PDF file exists and is readable.
        
        Args:
            pdf_path: Path to the PDF file
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a PDF
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")
        
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

    def get_library_name(self) -> str:
        """Get the name of the extraction library."""
        return self.library_name
