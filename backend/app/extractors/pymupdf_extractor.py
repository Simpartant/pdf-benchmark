"""PyMuPDF extractor implementation (interface only)."""

from pathlib import Path

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult


class PyMuPDFExtractor(BaseExtractor):
    """PyMuPDF (fitz) extraction implementation."""

    def __init__(self):
        super().__init__("pymupdf")

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract text using PyMuPDF library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        # TODO: Implement PyMuPDF extraction
        # This is just an interface placeholder
        return ExtractionResult(
            library_name=self.library_name,
            success=False,
            error_message="Extraction not implemented yet",
        )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract only text using PyMuPDF library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        # TODO: Implement actual PyMuPDF extraction
        # For now, return placeholder
        raise NotImplementedError("PyMuPDF extraction not implemented yet")
