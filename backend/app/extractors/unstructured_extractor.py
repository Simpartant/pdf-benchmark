"""Unstructured extractor implementation."""

import json
import base64
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    create_timestamped_output_directory,
    save_text_file,
    save_json_file,
    get_library_version,
    create_extraction_summary,
)


class UnstructuredExtractor(BaseExtractor):
    """
    Unstructured PDF extraction implementation.
    
    Extracts PDF content to multiple formats:
    - Markdown text
    - JSON structure
    - Images
    - Tables
    - Metadata
    
    Saves all outputs to results/{timestamp}/unstructured/
    """

    def __init__(self):
        super().__init__("unstructured")
        self._unstructured_available = self._check_unstructured_installation()

    def _check_unstructured_installation(self) -> bool:
        """Check if Unstructured is installed."""
        try:
            import unstructured
            try:
                from importlib.metadata import version
                unstructured_version = version("unstructured")
                logger.info(f"Unstructured available: version {unstructured_version}")
            except Exception:
                logger.info("Unstructured available (version unknown)")
            return True
        except ImportError:
            logger.warning("Unstructured not installed")
            return False
        except Exception as e:
            logger.warning(f"Unstructured import failed with unexpected error: {e}")
            return False

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract PDF with Unstructured (legacy method).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._unstructured_available:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="Unstructured is not installed. Install with: pip install unstructured[pdf]",
            )

        try:
            # Extract text for result
            text = self.extract_text(pdf_path)
            
            # Create result
            return ExtractionResult(
                library_name=self.library_name,
                success=True,
                text_content=text,
                metadata={"note": "Use extract_text() for full feature support"},
            )
            
        except Exception as e:
            logger.error(f"Unstructured extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
            )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text using Unstructured with full feature support.
        
        Extracts and saves:
        - Markdown text
        - JSON structure
        - Images
        - Tables
        - Metadata
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content (markdown format)
            
        Raises:
            ImportError: If Unstructured not installed
            Exception: For extraction errors
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._unstructured_available:
            raise ImportError("Unstructured is not installed. Install with: pip install unstructured[pdf]")

        try:
            # Suppress pi_heif import errors before importing unstructured
            import sys
            import unittest.mock as mock
            
            # Create a mock module for pi_heif if it's not available, as unstructured
            # tries to import it but it's optional
            try:
                import pi_heif  # noqa: F401
            except ImportError:
                logger.debug("pi_heif not available, creating mock module")
                mock_pi_heif = mock.MagicMock()
                mock_pi_heif.HeifFile = mock.MagicMock()
                sys.modules['pi_heif'] = mock_pi_heif
            
            # Import Unstructured components
            from unstructured.partition.pdf import partition_pdf
            from unstructured.staging.base import elements_to_json
            
            logger.info(f"Starting Unstructured extraction for {pdf_path}")
            start_time = datetime.now()
            
            # Create output directory
            output_dir = create_timestamped_output_directory(self.library_name, pdf_path)
            logger.info(f"Unstructured output directory: {output_dir}")
            
            # Partition PDF with full options
            elements = partition_pdf(
                filename=str(pdf_path),
                extract_images_in_pdf=True,
                extract_image_block_types=["Image", "Table"],
                extract_image_block_to_payload=True,
                strategy="hi_res",  # High resolution for better quality
                infer_table_structure=True,
                include_page_breaks=True,
            )
            
            logger.info(f"Extracted {len(elements)} elements from PDF")
            
            # Convert to different formats
            markdown_text = self._elements_to_markdown(elements)
            json_structure = self._elements_to_dict(elements)
            
            # Save outputs
            self._save_outputs(
                output_dir=output_dir,
                elements=elements,
                markdown_text=markdown_text,
                json_structure=json_structure,
            )
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Unstructured extraction completed in {extraction_time:.2f}s: "
                f"{len(markdown_text)} characters, outputs saved to {output_dir}"
            )
            
            return markdown_text
            
        except ImportError as e:
            logger.error(f"Unstructured import error: {e}")
            raise ImportError(f"Failed to import Unstructured: {e}")
            
        except Exception as e:
            logger.error(f"Unstructured extraction failed: {e}", exc_info=True)
            raise Exception(f"Unstructured extraction error: {e}")
        finally:
            # Clean up mock if it was added
            if 'pi_heif' in sys.modules and hasattr(sys.modules['pi_heif'], '_mock_return'):
                del sys.modules['pi_heif']

    def _elements_to_markdown(self, elements: list) -> str:
        """
        Convert Unstructured elements to markdown format.
        
        Args:
            elements: List of Unstructured elements
            
        Returns:
            Markdown formatted text
        """
        markdown_lines = []
        
        for element in elements:
            element_type = type(element).__name__
            text = str(element)
            
            if element_type == "Title":
                markdown_lines.append(f"# {text}\n")
            elif element_type == "NarrativeText":
                markdown_lines.append(f"{text}\n")
            elif element_type == "ListItem":
                markdown_lines.append(f"- {text}")
            elif element_type == "Table":
                # Tables are already formatted
                markdown_lines.append(f"\n{text}\n")
            elif element_type == "Image":
                markdown_lines.append(f"![Image]({element.metadata.filename if hasattr(element.metadata, 'filename') else 'image'})\n")
            elif element_type == "PageBreak":
                markdown_lines.append("\n---\n")
            else:
                markdown_lines.append(f"{text}\n")
        
        return "\n".join(markdown_lines)

    def _elements_to_dict(self, elements: list) -> List[Dict[str, Any]]:
        """
        Convert Unstructured elements to dictionary format.
        
        Args:
            elements: List of Unstructured elements
            
        Returns:
            List of element dictionaries
        """
        result = []
        
        for element in elements:
            element_dict = {
                "type": type(element).__name__,
                "text": str(element),
                "metadata": {}
            }
            
            # Add metadata if available
            if hasattr(element, "metadata"):
                metadata = element.metadata
                element_dict["metadata"] = {
                    "page_number": getattr(metadata, "page_number", None),
                    "filename": getattr(metadata, "filename", None),
                    "filetype": getattr(metadata, "filetype", None),
                    "coordinates": getattr(metadata, "coordinates", None),
                }
            
            result.append(element_dict)
        
        return result

    def _save_outputs(
        self,
        output_dir: Path,
        elements: list,
        markdown_text: str,
        json_structure: List[Dict[str, Any]],
    ) -> None:
        """
        Save all Unstructured outputs to directory.
        
        Saves:
        - markdown.md: Markdown text
        - elements.json: Structured elements
        - metadata.json: Document metadata
        - images/: Extracted images
        - tables/: Extracted tables
        
        Args:
            output_dir: Output directory path
            elements: List of Unstructured elements
            markdown_text: Markdown text content
            json_structure: Structured JSON data
        """
        try:
            # Save markdown
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            logger.debug(f"Saved markdown: {markdown_file}")
            
            # Save JSON structure
            json_file = output_dir / "elements.json"
            save_json_file(json_file, json_structure)
            logger.debug(f"Saved elements JSON: {json_file}")
            
            # Save metadata
            metadata_file = output_dir / "metadata.json"
            self._save_metadata(metadata_file, elements, markdown_text)
            logger.debug(f"Saved metadata: {metadata_file}")
            
            # Extract and save images
            images_dir = output_dir / "images"
            images_saved = self._save_images(images_dir, elements)
            if images_saved:
                logger.debug(f"Saved {images_saved} images to: {images_dir}")
            
            # Extract and save tables
            tables_dir = output_dir / "tables"
            tables_saved = self._save_tables(tables_dir, elements)
            if tables_saved:
                logger.debug(f"Saved {tables_saved} tables to: {tables_dir}")
            
            # Create summary file
            summary_file = output_dir / "summary.json"
            self._save_summary(summary_file, elements, markdown_text, images_saved, tables_saved)
            logger.debug(f"Saved summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving Unstructured outputs: {e}")
            # Don't raise - extraction succeeded even if save failed

    def _save_metadata(self, file_path: Path, elements: list, markdown_text: str) -> None:
        """Save document metadata."""
        try:
            # Count element types
            element_types = {}
            for element in elements:
                element_type = type(element).__name__
                element_types[element_type] = element_types.get(element_type, 0) + 1
            
            metadata = {
                "extractor": self.library_name,
                "extraction_time": datetime.now().isoformat(),
                "unstructured_version": get_library_version("unstructured"),
                "total_elements": len(elements),
                "element_types": element_types,
                "text_length": len(markdown_text),
                "word_count": len(markdown_text.split()),
            }
            
            save_json_file(file_path, metadata)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}", exc_info=True)

    def _save_images(self, images_dir: Path, elements: list) -> int:
        """
        Extract and save images from elements.
        
        Args:
            images_dir: Directory to save images
            elements: List of Unstructured elements
            
        Returns:
            Number of images saved
        """
        try:
            images_dir.mkdir(parents=True, exist_ok=True)
            images_saved = 0
            
            for element in elements:
                element_type = type(element).__name__
                
                if element_type == "Image":
                    try:
                        # Check if image has base64 data
                        if hasattr(element.metadata, "image_base64"):
                            image_data = base64.b64decode(element.metadata.image_base64)
                            image_file = images_dir / f"image_{images_saved:03d}.png"
                            
                            with open(image_file, "wb") as f:
                                f.write(image_data)
                            
                            images_saved += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to save image {images_saved}: {e}")
            
            return images_saved
            
        except Exception as e:
            logger.error(f"Error saving images: {e}")
            return 0

    def _save_tables(self, tables_dir: Path, elements: list) -> int:
        """
        Extract and save tables from elements.
        
        Args:
            tables_dir: Directory to save tables
            elements: List of Unstructured elements
            
        Returns:
            Number of tables saved
        """
        try:
            tables_dir.mkdir(parents=True, exist_ok=True)
            tables_saved = 0
            
            for element in elements:
                element_type = type(element).__name__
                
                if element_type == "Table":
                    try:
                        # Save table as JSON
                        table_data = {
                            "index": tables_saved,
                            "text": str(element),
                            "metadata": {}
                        }
                        
                        if hasattr(element, "metadata"):
                            table_data["metadata"] = {
                                "page_number": getattr(element.metadata, "page_number", None),
                                "text_as_html": getattr(element.metadata, "text_as_html", None),
                            }
                        
                        json_file = tables_dir / f"table_{tables_saved:03d}.json"
                        save_json_file(json_file, table_data)
                        
                        # Save table as markdown
                        md_file = tables_dir / f"table_{tables_saved:03d}.md"
                        save_text_file(md_file, str(element))
                        
                        tables_saved += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to save table {tables_saved}: {e}")
            
            return tables_saved
            
        except Exception as e:
            logger.error(f"Error saving tables: {e}")
            return 0

    def _save_summary(
        self,
        file_path: Path,
        elements: list,
        markdown_text: str,
        images_saved: int,
        tables_saved: int,
    ) -> None:
        """Save extraction summary."""
        try:
            # Count pages
            pages = set()
            for element in elements:
                if hasattr(element, "metadata") and hasattr(element.metadata, "page_number"):
                    if element.metadata.page_number:
                        pages.add(element.metadata.page_number)
            
            # Create output files description
            output_files = {
                "markdown": "markdown.md",
                "elements": "elements.json",
                "metadata": "metadata.json",
            }
            
            if images_saved > 0:
                output_files["images"] = f"images/ ({images_saved} files)"
            if tables_saved > 0:
                output_files["tables"] = f"tables/ ({tables_saved} files)"
            
            # Additional statistics
            additional_stats = {
                "total_elements": len(elements),
            }
            
            # Create standardized summary
            summary = create_extraction_summary(
                library_name=self.library_name,
                markdown_text=markdown_text,
                images_count=images_saved,
                tables_count=tables_saved,
                pages_count=len(pages),
                additional_stats=additional_stats,
                output_files=output_files,
            )
            
            # Add Unstructured version
            summary["unstructured_version"] = get_library_version("unstructured")
            
            save_json_file(file_path, summary)
                
        except Exception as e:
            logger.error(f"Failed to save summary: {e}", exc_info=True)
