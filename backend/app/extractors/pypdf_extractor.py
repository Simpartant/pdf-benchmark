"""PyPDF extractor implementation (interface only)."""

from pathlib import Path

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult


class PyPDFExtractor(BaseExtractor):
    """PyPDF extraction implementation."""

    def __init__(self):
        super().__init__("pypdf")

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract text using PyPDF library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        # TODO: Implement PyPDF extraction
        # This is just an interface placeholder
        return ExtractionResult(
            library_name=self.library_name,
            success=False,
            error_message="Extraction not implemented yet",
        )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract only text using PyPDF library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        # TODO: Implement actual PyPDF extraction
        # For now, return placeholder
        raise NotImplementedError("PyPDF extraction not implemented yet")
