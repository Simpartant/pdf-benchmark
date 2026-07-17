"""PyPDF extractor implementation."""

from pathlib import Path
from loguru import logger

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
        
        try:
            from pypdf import PdfReader
            
            # Read PDF
            reader = PdfReader(str(pdf_path))
            
            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            text = "\n".join(text_parts)
            
            return ExtractionResult(
                library_name=self.library_name,
                success=True,
                text_content=text,
                pages_extracted=len(reader.pages),
                char_count=len(text),
                word_count=len(text.split()),
            )
            
        except ImportError:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="PyPDF is not installed. Install with: pip install pypdf",
            )
        except Exception as e:
            logger.error(f"PyPDF extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
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
        
        try:
            from pypdf import PdfReader
            
            # Read PDF
            reader = PdfReader(str(pdf_path))
            
            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            return "\n".join(text_parts)
            
        except ImportError:
            raise ImportError("PyPDF is not installed. Install with: pip install pypdf")
        except Exception as e:
            logger.error(f"PyPDF extraction failed: {e}")
            raise
