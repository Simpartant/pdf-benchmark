"""Unstructured extractor implementation (normalized interface)."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    save_text_file,
    save_json_file,
    create_extraction_summary,
)


class UnstructuredExtractor(BaseExtractor):
    """
    Unstructured PDF extraction implementation.

    Extracts PDF content to markdown, structured elements, images and
    tables and returns a single normalized :class:`ExtractionResult`.
    """

    library_id = "unstructured"
    display_name = "Unstructured"
    description = "Universal document processing library with element-based extraction"
    capabilities = [
        "text_extraction",
        "markdown_export",
        "json_export",
        "image_extraction",
        "table_extraction",
        "element_classification",
        "layout_analysis",
        "metadata_extraction",
    ]
    performance_notes = "Element-based extraction with configurable strategies"
    required_modules = ["unstructured", "unstructured.partition.pdf"]

    # Supported strategies
    STRATEGIES = ["auto", "fast", "hi_res", "ocr_only"]
    DEFAULT_STRATEGY = "auto"

    def __init__(self):
        super().__init__()
        self._unstructured_available = self.is_available()

    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Extract PDF with Unstructured into a normalized ExtractionResult."""
        self.validate_pdf(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self._unstructured_available:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="Unstructured is not installed. Install with: pip install unstructured[local-inference]",
                output_files={},
            )

        # Get strategy from options, default to "auto"
        strategy = (options or {}).get("strategy", self.DEFAULT_STRATEGY)
        if strategy not in self.STRATEGIES:
            strategy = self.DEFAULT_STRATEGY

        try:
            elements = self._partition(pdf_path, strategy)
            markdown_text = self._elements_to_markdown(elements)
            json_structure = self._elements_to_dict(elements)

            output_files = self._save_outputs(
                output_dir, elements, markdown_text, json_structure, strategy
            )

            pages = set()
            for element in elements:
                if hasattr(element, "metadata") and hasattr(
                    element.metadata, "page_number"
                ):
                    if element.metadata.page_number:
                        pages.add(element.metadata.page_number)

            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="success",
                markdown=markdown_text,
                structured_json={"elements": json_structure},
                metadata={"extractor": self.library_id, "strategy": strategy},
                page_count=len(pages),
                table_count=sum(
                    1 for e in elements if type(e).__name__ == "Table"
                ),
                image_count=sum(
                    1 for e in elements if type(e).__name__ == "Image"
                ),
                output_files=output_files,
            )
        except Exception as e:
            logger.error(f"Unstructured extraction failed: {e}", exc_info=True)
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=str(e),
                output_files={},
            )

    def _partition(self, pdf_path: Path, strategy: str):
        """Partition PDF using Unstructured with the specified strategy."""
        from unstructured.partition.pdf import partition_pdf

        # Build kwargs based on strategy
        partition_kwargs = {
            "filename": str(pdf_path),
            "strategy": strategy,
        }

        # Add strategy-specific options
        if strategy == "hi_res":
            partition_kwargs["infer_table_structure"] = True
            partition_kwargs["extract_images_in_pdf"] = True
            partition_kwargs["extract_image_block_types"] = ["Image", "Table"]
            partition_kwargs["extract_image_block_to_payload"] = False
        elif strategy == "ocr_only":
            partition_kwargs["extract_images_in_pdf"] = True
            partition_kwargs["extract_image_block_types"] = ["Image"]
        elif strategy == "fast":
            partition_kwargs["infer_table_structure"] = False
        elif strategy == "auto":
            partition_kwargs["infer_table_structure"] = True
            partition_kwargs["extract_images_in_pdf"] = True
            partition_kwargs["extract_image_block_types"] = ["Image", "Table"]

        return partition_pdf(**partition_kwargs)

    def _elements_to_markdown(self, elements: list) -> str:
        """Convert Unstructured elements to markdown format."""
        lines = []
        for element in elements:
            element_type = type(element).__name__
            text = str(element)
            if element_type == "Title":
                lines.append(f"# {text}\n")
            elif element_type == "ListItem":
                lines.append(f"- {text}")
            elif element_type in ("Table", "Image"):
                lines.append(f"\n{text}\n")
            elif element_type == "PageBreak":
                lines.append("\n---\n")
            else:
                lines.append(f"{text}\n")
        return "\n".join(lines)

    def _elements_to_dict(self, elements: list) -> List[Dict[str, Any]]:
        """Convert Unstructured elements to dictionary format preserving metadata."""
        result = []
        for element in elements:
            element_dict: Dict[str, Any] = {
                "type": type(element).__name__,
                "text": str(element),
            }
            if hasattr(element, "metadata"):
                # Convert coordinates to serializable format
                coords = getattr(element.metadata, "coordinates", None)
                coords_dict = None
                if coords is not None:
                    try:
                        system = coords.system
                        system_str = system.__class__.__name__ if system else None
                        coords_dict = {
                            "points": [list(p) for p in coords.points] if hasattr(coords, "points") else None,
                            "system": system_str,
                        }
                    except Exception:
                        coords_dict = str(coords)

                element_dict["metadata"] = {
                    "page_number": getattr(element.metadata, "page_number", None),
                    "filename": getattr(element.metadata, "filename", None),
                    "coordinates": coords_dict,
                }
            result.append(element_dict)
        return result

    def _save_outputs(
        self,
        output_dir: Path,
        elements: list,
        markdown_text: str,
        json_structure: List[Dict[str, Any]],
        strategy: str,
    ) -> Dict[str, Any]:
        """Save extraction outputs to files."""
        output_files: Dict[str, Any] = {}
        try:
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            output_files["markdown"] = str(markdown_file)

            json_file = output_dir / "elements.json"
            save_json_file(json_file, json_structure)
            output_files["json"] = str(json_file)

            metadata_file = output_dir / "metadata.json"
            save_json_file(
                metadata_file,
                {
                    "extractor": self.library_id,
                    "strategy": strategy,
                    "total_elements": len(elements),
                },
            )
            output_files["metadata"] = str(metadata_file)

            summary_file = output_dir / "summary.json"
            save_json_file(
                summary_file,
                create_extraction_summary(
                    library_name=self.library_id,
                    markdown_text=markdown_text,
                    images_count=sum(
                        1 for e in elements if type(e).__name__ == "Image"
                    ),
                    tables_count=sum(
                        1 for e in elements if type(e).__name__ == "Table"
                    ),
                    pages_count=len(
                        {
                            getattr(e.metadata, "page_number", None)
                            for e in elements
                            if hasattr(e, "metadata")
                            and getattr(e.metadata, "page_number", None)
                        }
                    ),
                    output_files=output_files,
                ),
            )
            output_files["summary"] = str(summary_file)
        except Exception as e:
            logger.error(f"Error saving Unstructured outputs: {e}")
        return output_files