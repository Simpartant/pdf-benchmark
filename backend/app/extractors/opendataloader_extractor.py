"""OpenDataLoader extractor implementation (normalized interface)."""

import json
import subprocess
import shutil
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


class OpenDataLoaderExtractor(BaseExtractor):
    """
    OpenDataLoader PDF extraction implementation.

    Extracts PDF content to markdown, JSON (with bounding boxes), and HTML.
    Uses the official opendataloader-pdf package which requires Java 11+.
    """

    library_id = "opendataloader"
    display_name = "OpenDataLoader"
    description = "PDF parser for AI-ready data with bounding boxes and reading order"
    capabilities = [
        "text_extraction",
        "markdown_export",
        "json_export",
        "html_export",
        "image_extraction",
        "table_extraction",
        "layout_analysis",
        "metadata_extraction",
        "bounding_boxes",
    ]
    performance_notes = "Deterministic local mode with Java backend, #1 in extraction benchmarks"
    required_modules = ["opendataloader_pdf"]

    def __init__(self):
        super().__init__()
        self._opendataloader_available = self.is_available()
        self._java_available = self._check_java()

    def _check_java(self) -> bool:
        """Check if Java 11+ is available."""
        import os
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # java -version outputs to stderr
            version_output = result.stderr or result.stdout
            # Check for Java 11+ (versions 11, 17, 18, 19, 20, 21, etc.)
            # The version string format is like "openjdk version "11.0.22" ..."
            import re
            match = re.search(r'version\s+"(\d+)', version_output)
            if match:
                major_version = int(match.group(1))
                return major_version >= 11
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_java_version(self) -> str:
        """Get the Java version string for diagnostics."""
        import os
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version_output = result.stderr or result.stdout
            import re
            match = re.search(r'version\s+"([^"]+)"', version_output)
            if match:
                return match.group(1)
            return "unknown"
        except (subprocess.SubprocessError, FileNotFoundError):
            return "not installed"

    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Extract PDF with OpenDataLoader into a normalized ExtractionResult."""
        self.validate_pdf(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self._opendataloader_available:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="OpenDataLoader is not installed. Install with: pip install opendataloader-pdf",
                output_files={},
            )

        if not self._java_available:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="Java 11+ is required for OpenDataLoader. Install from https://adoptium.net/",
                output_files={},
            )

        # Get options
        generate_html = (options or {}).get("generate_html", False)

        try:
            # Run opendataloader via the Python wrapper
            import opendataloader_pdf

            opendataloader_pdf.run(
                input_path=str(pdf_path),
                output_folder=str(output_dir),
                generate_markdown=True,
                generate_html=generate_html,
                no_json=False,
            )

            # Load the generated outputs
            output_files = self._load_outputs(output_dir)
            markdown_text = self._read_markdown(output_dir)
            json_data = self._read_json(output_dir)

            # Extract metrics from OpenDataLoader JSON structure
            page_count, table_count, image_count = self._extract_metrics(json_data)

            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="success",
                markdown=markdown_text,
                structured_json={"opendataloader": json_data},
                metadata={"extractor": self.library_id, "generate_html": generate_html},
                page_count=page_count,
                table_count=table_count,
                image_count=image_count,
                output_files=output_files,
            )
        except Exception as e:
            logger.error(f"OpenDataLoader extraction failed: {e}", exc_info=True)
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=str(e),
                output_files={},
            )

    def _load_outputs(self, output_dir: Path) -> Dict[str, Any]:
        """Load paths to generated output files."""
        output_files: Dict[str, Any] = {}
        for ext, key in [(".md", "markdown"), (".json", "json"), (".html", "html")]:
            for f in output_dir.glob(f"*{ext}"):
                if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                    output_files[key] = str(f)
        return output_files

    def _read_markdown(self, output_dir: Path) -> str:
        """Read the generated markdown file."""
        for f in output_dir.glob("*.md"):
            if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                with open(f, "r", encoding="utf-8") as mf:
                    return mf.read()
        return ""

    def _read_json(self, output_dir: Path) -> Dict[str, Any]:
        """Read the generated JSON file."""
        for f in output_dir.glob("*.json"):
            if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                with open(f, "r", encoding="utf-8") as jf:
                    return json.load(jf)
        return {}

    def _extract_metrics(self, json_data: Dict[str, Any]) -> tuple:
        """Extract page count, table count, and image count from OpenDataLoader JSON."""
        pages = set()
        table_count = 0
        image_count = 0

        # OpenDataLoader uses "kids" array for elements
        kids = json_data.get("kids", [])
        for item in kids:
            if isinstance(item, dict):
                # Page number is in "page number" field
                if "page number" in item:
                    pages.add(item["page number"])
                # Type is in "type" field
                item_type = item.get("type", "").lower()
                if item_type == "table":
                    table_count += 1
                elif item_type == "image":
                    image_count += 1

        return len(pages), table_count, image_count

    def _save_outputs(
        self,
        output_dir: Path,
        documents: list,
        markdown_text: str,
        json_structure: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Save additional metadata and summary files."""
        output_files: Dict[str, Any] = {}
        try:
            metadata_file = output_dir / "metadata.json"
            save_json_file(
                metadata_file,
                {
                    "extractor": self.library_id,
                    "total_documents": len(documents),
                },
            )
            output_files["metadata"] = str(metadata_file)

            summary_file = output_dir / "summary.json"
            save_json_file(
                summary_file,
                create_extraction_summary(
                    library_name=self.library_id,
                    markdown_text=markdown_text,
                    images_count=0,
                    tables_count=0,
                    pages_count=0,
                    output_files=output_files,
                ),
            )
            output_files["summary"] = str(summary_file)
        except Exception as e:
            logger.error(f"Error saving OpenDataLoader outputs: {e}")
        return output_files