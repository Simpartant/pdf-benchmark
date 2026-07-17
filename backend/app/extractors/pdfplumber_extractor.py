"""PDFPlumber extractor implementation."""

from pathlib import Path
from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult


class PDFPlumberExtractor(BaseExtractor):
    """PDFPlumber extraction implementation."""

    def __init__(self):
        super().__init__("pdfplumber")

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract text using PDFPlumber library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        try:
            import pdfplumber
            
            # Open PDF with pdfplumber
            with pdfplumber.open(str(pdf_path)) as pdf:
                # Extract text from all pages
                text_parts = []
                tables_count = 0
                
                for page in pdf.pages:
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    
                    # Count tables
                    tables = page.extract_tables()
                    if tables:
                        tables_count += len(tables)
                
                text = "\n".join(text_parts)
                
                return ExtractionResult(
                    library_name=self.library_name,
                    success=True,
                    text_content=text,
                    pages_extracted=len(pdf.pages),
                    char_count=len(text),
                    word_count=len(text.split()),
                    tables_count=tables_count,
                )
            
        except ImportError:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="PDFPlumber is not installed. Install with: pip install pdfplumber",
            )
        except Exception as e:
            logger.error(f"PDFPlumber extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
            )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract only text using PDFPlumber library.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        try:
            import pdfplumber
            
            # Open PDF with pdfplumber
            with pdfplumber.open(str(pdf_path)) as pdf:
                # Extract text from all pages
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return "\n".join(text_parts)
            
        except ImportError:
            raise ImportError("PDFPlumber is not installed. Install with: pip install pdfplumber")
        except Exception as e:
            logger.error(f"PDFPlumber extraction failed: {e}")
            raise
