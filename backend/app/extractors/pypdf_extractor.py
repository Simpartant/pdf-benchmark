"""PyPDF extractor implementation (normalized interface)."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    save_text_file,
    save_json_file,
    create_extraction_summary,
)


class PyPDFExtractor(BaseExtractor):
    """PyPDF extraction implementation."""

    library_id = "pypdf"
    display_name = "PyPDF"
    description = "Pure Python PDF library with good stability"
    capabilities = ["text_extraction", "metadata"]
    performance_notes = "Good for simple PDFs, slower on complex layouts"
    required_modules = ["pypdf"]

    def __init__(self):
        super().__init__()

    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Extract PDF with PyPDF into a normalized ExtractionResult."""
        self.validate_pdf(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            from pypdf import PdfReader

            reader = PdfReader(str(pdf_path))
            pages = len(reader.pages)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)

            full_text = "\n\n".join(text_parts)

            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, full_text)
            json_file = output_dir / "document.json"
            save_json_file(json_file, {"pages": pages, "text": full_text})
            summary_file = output_dir / "summary.json"
            save_json_file(
                summary_file,
                create_extraction_summary(
                    library_name=self.library_id,
                    markdown_text=full_text,
                    pages_count=pages,
                    output_files={
                        "markdown": str(markdown_file),
                        "json": str(json_file),
                    },
                ),
            )

            return ExtractionResult(
                library=self.library_id,
                original_filename=pdf_path.name,
                status="success",
                markdown=full_text,
                structured_json={"pages": pages},
                page_count=pages,
                output_files={
                    "markdown": str(markdown_file),
                    "json": str(json_file),
                },
            )
        except Exception as e:
            logger.exception(f"PyPDF extraction failed: {e}")
            return ExtractionResult(
                library=self.library_id,
                original_filename=pdf_path.name,
                status="failed",
                error=str(e),
            )
