"""Docling extractor implementation (normalized interface)."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger

from app.extractors.base_extractor import BaseExtractor, AvailabilityStatus
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    save_text_file,
    save_json_file,
    get_library_version,
    create_extraction_summary,
)


class DoclingExtractor(BaseExtractor):
    """
    Docling PDF extraction implementation.

    Uses the official Docling API to extract PDF content to multiple
    formats (markdown, JSON, images, tables, metadata) and returns a
    single normalized :class:`ExtractionResult`.
    """

    library_id = "docling"
    display_name = "Docling"
    description = "Advanced document understanding and conversion library"
    capabilities = [
        "text_extraction",
        "markdown_export",
        "json_export",
        "image_extraction",
        "table_extraction",
        "layout_analysis",
        "metadata_extraction",
    ]
    performance_notes = "Comprehensive extraction with multiple output formats"
    required_modules = ["docling"]

    def __init__(self):
        super().__init__()
        self._docling_available = self.is_available()

    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        Extract PDF with Docling into a normalized ExtractionResult.

        Args:
            pdf_path: Path to the source PDF file.
            output_dir: Directory where extraction artifacts are written.
            options: Optional extractor-specific options (unused for now).

        Returns:
            ExtractionResult populated with markdown, structured JSON,
            counts, output files and status.
        """
        self.validate_pdf(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self._docling_available:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="Docling is not installed. Install with: pip install docling",
                output_files={},
            )

        try:
            markdown_text, structured_json, images, tables = self._run_docling(
                pdf_path, output_dir
            )

            output_files = self._save_outputs(
                output_dir=output_dir,
                markdown_text=markdown_text,
                structured_json=structured_json,
                images=images,
                tables=tables,
            )

            page_count = structured_json.get("page_count", 0) if isinstance(
                structured_json, dict
            ) else 0

            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="success",
                markdown=markdown_text,
                structured_json=structured_json,
                metadata={"extractor": self.library_id},
                page_count=page_count,
                table_count=tables,
                image_count=images,
                output_files=output_files,
            )

        except Exception as e:
            logger.error(f"Docling extraction failed: {e}", exc_info=True)
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=str(e),
                output_files={},
            )

    # ------------------------------------------------------------------
    # Internal Docling logic (preserves previous behavior)
    # ------------------------------------------------------------------
    def _run_docling(self, pdf_path: Path, output_dir: Path):
        """Run Docling conversion and return (markdown, json, n_images, n_tables)."""
        from docling.document_converter import DocumentConverter

        logger.info(f"Starting Docling extraction for {pdf_path}")
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))

        if not result or not hasattr(result, "document"):
            raise Exception("Docling conversion returned invalid result")

        markdown_text = result.document.export_to_markdown() or ""

        structured_json = {}
        try:
            structured_json = result.document.export_to_dict()
        except Exception as e:
            logger.debug(f"Could not export Docling JSON: {e}")

        # Page count
        page_count = 0
        if hasattr(result.document, "pages"):
            page_count = len(result.document.pages)
        structured_json = structured_json or {}
        structured_json["page_count"] = page_count

        images = self._count_images(result.document)
        tables = self._count_tables(result.document)

        return markdown_text, structured_json, images, tables

    def _count_images(self, doc) -> int:
        count = 0
        for attr in ("pictures", "images", "figures"):
            val = getattr(doc, attr, None)
            if val:
                count += len(val)
        if hasattr(doc, "pages"):
            for page in doc.pages:
                for attr in ("images", "pictures"):
                    val = getattr(page, attr, None)
                    if val:
                        count += len(val)
        return count

    def _count_tables(self, doc) -> int:
        count = 0
        if hasattr(doc, "tables") and doc.tables:
            count += len(doc.tables)
        if hasattr(doc, "pages"):
            for page in doc.pages:
                if hasattr(page, "tables") and page.tables:
                    count += len(page.tables)
        return count

    def _save_outputs(
        self,
        output_dir: Path,
        markdown_text: str,
        structured_json: Dict[str, Any],
        images: int,
        tables: int,
    ) -> Dict[str, Any]:
        """Persist markdown, JSON and a summary; return output file map."""
        output_files: Dict[str, Any] = {}

        try:
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            output_files["markdown"] = str(markdown_file)

            json_file = output_dir / "document.json"
            save_json_file(json_file, structured_json)
            output_files["json"] = str(json_file)

            metadata_file = output_dir / "metadata.json"
            metadata = {
                "extractor": self.library_id,
                "extraction_time": datetime.now().isoformat(),
                "docling_version": get_library_version("docling"),
                "page_count": structured_json.get("page_count", 0),
                "image_count": images,
                "table_count": tables,
            }
            save_json_file(metadata_file, metadata)
            output_files["metadata"] = str(metadata_file)

            summary_file = output_dir / "summary.json"
            summary = create_extraction_summary(
                library_name=self.library_id,
                markdown_text=markdown_text,
                images_count=images,
                tables_count=tables,
                pages_count=structured_json.get("page_count", 0),
                output_files=output_files,
            )
            save_json_file(summary_file, summary)
            output_files["summary"] = str(summary_file)
        except Exception as e:
            logger.error(f"Error saving Docling outputs: {e}")

        return output_files