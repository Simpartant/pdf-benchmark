"""PyMuPDF extractor implementation."""

from pathlib import Path
from loguru import logger

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
        
        try:
            import pymupdf  # imports as 'fitz' internally
            
            # Open PDF
            doc = pymupdf.open(str(pdf_path))
            
            # Extract text from all pages
            text_parts = []
            images_count = 0
            
            for page in doc:
                # Extract text
                page_text = page.get_text()
                text_parts.append(page_text)
                
                # Count images
                images = page.get_images()
                if images:
                    images_count += len(images)
            
            text = "\n".join(text_parts)
            
            # Close document
            doc.close()
            
            return ExtractionResult(
                library_name=self.library_name,
                success=True,
                text_content=text,
                pages_extracted=len(doc),
                char_count=len(text),
                word_count=len(text.split()),
                images_count=images_count,
            )
            
        except ImportError:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="PyMuPDF is not installed. Install with: pip install pymupdf",
            )
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
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
        
        try:
            import pymupdf  # imports as 'fitz' internally
            
            # Open PDF
            doc = pymupdf.open(str(pdf_path))
            
            # Extract text from all pages
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            
            text = "\n".join(text_parts)
            
            # Close document
            doc.close()
            
            return text
            
        except ImportError:
            raise ImportError("PyMuPDF is not installed. Install with: pip install pymupdf")
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise
