"""Docling extractor implementation."""

import json
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List
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


class DoclingExtractor(BaseExtractor):
    """
    Docling PDF extraction implementation.
    
    Uses the official Docling API to extract PDF content to multiple formats:
    - Markdown text
    - JSON structure
    - Images
    - Tables
    - Metadata
    
    Saves all outputs to results/{timestamp}/docling/
    """

    def __init__(self):
        super().__init__("docling")
        self._docling_available = self._check_docling_installation()

    def _check_docling_installation(self) -> bool:
        """Check if Docling is installed."""
        try:
            import docling
            logger.info(f"Docling available: version {docling.__version__}")
            return True
        except ImportError:
            logger.warning("Docling not installed")
            return False

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract PDF with Docling (legacy method).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._docling_available:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="Docling is not installed. Install with: pip install docling",
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
            logger.error(f"Docling extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
            )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text using Docling with full feature support.
        
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
            ImportError: If Docling not installed
            Exception: For extraction errors
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._docling_available:
            raise ImportError("Docling is not installed. Install with: pip install docling")

        try:
            # Import Docling components
            from docling.document_converter import DocumentConverter
            
            logger.info(f"Starting Docling extraction for {pdf_path}")
            start_time = datetime.now()
            
            # Create output directory
            output_dir = create_timestamped_output_directory(self.library_name, pdf_path)
            logger.info(f"Docling output directory: {output_dir}")
            
            # Initialize converter with default settings
            converter = DocumentConverter()
            
            # Convert PDF - Docling processes the entire document
            logger.debug("Converting PDF with Docling...")
            result = converter.convert(str(pdf_path))
            
            if not result or not hasattr(result, 'document'):
                raise Exception("Docling conversion returned invalid result")
            
            # Extract markdown text
            logger.debug("Exporting to markdown...")
            markdown_text = result.document.export_to_markdown()
            
            if not markdown_text:
                logger.warning("Docling returned empty markdown text")
                markdown_text = ""
            
            # Save all outputs
            self._save_outputs(
                output_dir=output_dir,
                result=result,
                markdown_text=markdown_text,
            )
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Docling extraction completed in {extraction_time:.2f}s: "
                f"{len(markdown_text)} characters, outputs saved to {output_dir}"
            )
            
            return markdown_text
            
        except ImportError as e:
            logger.error(f"Docling import error: {e}")
            raise ImportError(f"Failed to import Docling: {e}")
            
        except Exception as e:
            logger.error(f"Docling extraction failed: {e}", exc_info=True)
            raise Exception(f"Docling extraction error: {e}")

    def _save_outputs(
        self,
        output_dir: Path,
        result: Any,
        markdown_text: str,
    ) -> None:
        """
        Save all Docling outputs to directory.
        
        Saves:
        - markdown.md: Markdown text
        - document.json: JSON structure
        - metadata.json: Document metadata
        - images/: Extracted images
        - tables/: Extracted tables
        
        Args:
            output_dir: Output directory path
            result: Docling conversion result
            markdown_text: Markdown text content
        """
        try:
            # Save markdown
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            logger.debug(f"Saved markdown: {markdown_file}")
            
            # Save JSON structure
            json_file = output_dir / "document.json"
            self._save_json_structure(json_file, result)
            logger.debug(f"Saved JSON structure: {json_file}")
            
            # Save metadata
            metadata_file = output_dir / "metadata.json"
            self._save_metadata(metadata_file, result)
            logger.debug(f"Saved metadata: {metadata_file}")
            
            # Extract and save images
            images_dir = output_dir / "images"
            images_saved = self._save_images(images_dir, result)
            if images_saved:
                logger.debug(f"Saved {images_saved} images to: {images_dir}")
            
            # Extract and save tables
            tables_dir = output_dir / "tables"
            tables_saved = self._save_tables(tables_dir, result)
            if tables_saved:
                logger.debug(f"Saved {tables_saved} tables to: {tables_dir}")
            
            # Create summary file
            summary_file = output_dir / "summary.json"
            self._save_summary(summary_file, result, markdown_text, images_saved, tables_saved)
            logger.debug(f"Saved summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving Docling outputs: {e}")
            # Don't raise - extraction succeeded even if save failed

    def _save_json_structure(self, file_path: Path, result: Any) -> None:
        """Save document JSON structure."""
        try:
            # Export to JSON
            json_data = result.document.export_to_dict()
            save_json_file(file_path, json_data)
                
        except Exception as e:
            logger.error(f"Failed to save JSON structure: {e}")

    def _save_metadata(self, file_path: Path, result: Any) -> None:
        """Save document metadata."""
        try:
            metadata = {
                "extractor": self.library_name,
                "extraction_time": datetime.now().isoformat(),
                "docling_version": get_library_version("docling"),
            }
            
            # Add source information
            if hasattr(result, 'input'):
                if hasattr(result.input, 'file'):
                    metadata["source_file"] = str(result.input.file)
                if hasattr(result.input, 'format'):
                    metadata["source_format"] = result.input.format
            
            # Add document information
            if hasattr(result, 'document'):
                doc = result.document
                
                # Page count
                if hasattr(doc, 'pages'):
                    metadata["num_pages"] = len(doc.pages)
                
                # Document metadata
                if hasattr(doc, 'metadata'):
                    try:
                        if isinstance(doc.metadata, dict):
                            metadata["document_metadata"] = doc.metadata
                        else:
                            metadata["document_metadata"] = str(doc.metadata)
                    except Exception as e:
                        logger.debug(f"Could not extract document metadata: {e}")
                
                # Content statistics
                if hasattr(doc, 'text'):
                    metadata["total_text_length"] = len(doc.text)
                
                # Count content types
                content_counts = {}
                if hasattr(doc, 'tables'):
                    content_counts["tables"] = len(doc.tables) if doc.tables else 0
                if hasattr(doc, 'pictures'):
                    content_counts["pictures"] = len(doc.pictures) if doc.pictures else 0
                if hasattr(doc, 'images'):
                    content_counts["images"] = len(doc.images) if doc.images else 0
                if hasattr(doc, 'figures'):
                    content_counts["figures"] = len(doc.figures) if doc.figures else 0
                    
                if content_counts:
                    metadata["content_counts"] = content_counts
            
            save_json_file(file_path, metadata)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}", exc_info=True)

    def _save_images(self, images_dir: Path, result: Any) -> int:
        """
        Extract and save images from document.
        
        Args:
            images_dir: Directory to save images
            result: Docling result
            
        Returns:
            Number of images saved
        """
        images_saved = 0
        
        try:
            # Docling stores images in the document structure
            if not hasattr(result, 'document'):
                logger.debug("No document in result")
                return 0
            
            doc = result.document
            
            # Try different ways to access images in Docling
            images = []
            
            # Method 1: Check for pictures attribute
            if hasattr(doc, 'pictures') and doc.pictures:
                logger.debug(f"Found {len(doc.pictures)} pictures in document")
                images.extend(doc.pictures)
            
            # Method 2: Check for images attribute
            if hasattr(doc, 'images') and doc.images:
                logger.debug(f"Found {len(doc.images)} images in document")
                images.extend(doc.images)
            
            # Method 3: Extract from pages
            if hasattr(doc, 'pages'):
                for page_idx, page in enumerate(doc.pages):
                    if hasattr(page, 'images') and page.images:
                        logger.debug(f"Found {len(page.images)} images on page {page_idx}")
                        images.extend(page.images)
                    if hasattr(page, 'pictures') and page.pictures:
                        logger.debug(f"Found {len(page.pictures)} pictures on page {page_idx}")
                        images.extend(page.pictures)
            
            if not images:
                logger.debug("No images found in document")
                return 0
            
            # Create images directory
            images_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Processing {len(images)} images...")
            
            # Save each image
            for idx, image_obj in enumerate(images):
                try:
                    image_file = images_dir / f"image_{idx:03d}.png"
                    
                    # Try different ways to get image data
                    saved = False
                    
                    # Method 1: PIL Image object
                    if hasattr(image_obj, 'image') and image_obj.image:
                        try:
                            from PIL import Image
                            if isinstance(image_obj.image, Image.Image):
                                image_obj.image.save(str(image_file))
                                saved = True
                                logger.debug(f"Saved image {idx} as PIL Image")
                        except Exception as e:
                            logger.debug(f"Failed to save as PIL Image: {e}")
                    
                    # Method 2: Binary data
                    if not saved and hasattr(image_obj, 'data'):
                        try:
                            with open(image_file, "wb") as f:
                                f.write(image_obj.data)
                            saved = True
                            logger.debug(f"Saved image {idx} from binary data")
                        except Exception as e:
                            logger.debug(f"Failed to save from binary data: {e}")
                    
                    # Method 3: Base64 data
                    if not saved and hasattr(image_obj, 'base64'):
                        try:
                            img_data = base64.b64decode(image_obj.base64)
                            with open(image_file, "wb") as f:
                                f.write(img_data)
                            saved = True
                            logger.debug(f"Saved image {idx} from base64")
                        except Exception as e:
                            logger.debug(f"Failed to save from base64: {e}")
                    
                    # Method 4: URI/path reference
                    if not saved and hasattr(image_obj, 'uri'):
                        try:
                            import shutil
                            shutil.copy(image_obj.uri, image_file)
                            saved = True
                            logger.debug(f"Saved image {idx} from URI")
                        except Exception as e:
                            logger.debug(f"Failed to save from URI: {e}")
                    
                    if saved:
                        images_saved += 1
                    else:
                        logger.warning(f"Could not save image {idx}: no valid data source found")
                        
                except Exception as e:
                    logger.warning(f"Failed to save image {idx}: {e}")
                    
            logger.info(f"Saved {images_saved}/{len(images)} images")
            return images_saved
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}", exc_info=True)
            return images_saved

    def _save_tables(self, tables_dir: Path, result: Any) -> int:
        """
        Extract and save tables from document.
        
        Args:
            tables_dir: Directory to save tables
            result: Docling result
            
        Returns:
            Number of tables saved
        """
        tables_saved = 0
        
        try:
            if not hasattr(result, 'document'):
                logger.debug("No document in result")
                return 0
            
            doc = result.document
            
            # Collect tables from different sources
            tables = []
            
            # Method 1: Direct tables attribute
            if hasattr(doc, 'tables') and doc.tables:
                logger.debug(f"Found {len(doc.tables)} tables in document")
                tables.extend(doc.tables)
            
            # Method 2: Extract from pages
            if hasattr(doc, 'pages'):
                for page_idx, page in enumerate(doc.pages):
                    if hasattr(page, 'tables') and page.tables:
                        logger.debug(f"Found {len(page.tables)} tables on page {page_idx}")
                        tables.extend(page.tables)
            
            if not tables:
                logger.debug("No tables found in document")
                return 0
            
            # Create tables directory
            tables_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Processing {len(tables)} tables...")
            
            # Save each table
            for idx, table in enumerate(tables):
                try:
                    # Save as JSON
                    json_file = tables_dir / f"table_{idx:03d}.json"
                    table_data = self._extract_table_data(table, idx)
                        save_json_file(json_file, table_data)
                        logger.debug(f"Saved table {idx} as JSON")
                        
                        # Save as Markdown if available
                        md_file = tables_dir / f"table_{idx:03d}.md"
                        markdown_content = self._export_table_to_markdown(table)
                        
                        if markdown_content:
                            save_text_file(md_file, markdown_content)
                            logger.debug(f"Saved table {idx} as Markdown")
                        
                        # Save as CSV if possible
                        csv_file = tables_dir / f"table_{idx:03d}.csv"
                        csv_content = self._export_table_to_csv(table)
                        
                        if csv_content:
                            save_text_file(csv_file, csv_content)
                except Exception as e:
                    logger.warning(f"Failed to save table {idx}: {e}")
                    
            logger.info(f"Saved {tables_saved} tables")
            return tables_saved
            
        except Exception as e:
            logger.error(f"Error extracting tables: {e}", exc_info=True)
            return tables_saved

    def _extract_table_data(self, table: Any, index: int) -> Dict[str, Any]:
        """Extract table data into dictionary format."""
        table_data = {
            "index": index,
            "type": "table",
        }
        
        try:
            # Try to export to dict
            if hasattr(table, 'export_to_dict'):
                table_data["data"] = table.export_to_dict()
            elif hasattr(table, 'to_dict'):
                table_data["data"] = table.to_dict()
            elif hasattr(table, 'data'):
                table_data["data"] = table.data
            else:
                # Fallback: try to extract rows/cells
                if hasattr(table, 'rows'):
                    table_data["data"] = {
                        "rows": [self._extract_row_data(row) for row in table.rows]
                    }
                elif hasattr(table, 'cells'):
                    table_data["data"] = {
                        "cells": [self._extract_cell_data(cell) for cell in table.cells]
                    }
                else:
                    table_data["data"] = str(table)
            
            # Add metadata
            if hasattr(table, 'num_rows'):
                table_data["num_rows"] = table.num_rows
            if hasattr(table, 'num_cols'):
                table_data["num_cols"] = table.num_cols
            if hasattr(table, 'bbox'):
                table_data["bbox"] = table.bbox
                
        except Exception as e:
            logger.debug(f"Error extracting table data: {e}")
            table_data["data"] = str(table)
            
        return table_data

    def _extract_row_data(self, row: Any) -> Any:
        """Extract row data."""
        try:
            if hasattr(row, 'cells'):
                return [self._extract_cell_data(cell) for cell in row.cells]
            elif hasattr(row, 'to_dict'):
                return row.to_dict()
            else:
                return str(row)
        except Exception:
            return str(row)

    def _extract_cell_data(self, cell: Any) -> Any:
        """Extract cell data."""
        try:
            if hasattr(cell, 'text'):
                return cell.text
            elif hasattr(cell, 'value'):
                return cell.value
            elif hasattr(cell, 'to_dict'):
                return cell.to_dict()
            else:
                return str(cell)
        except Exception:
            return str(cell)

    def _export_table_to_markdown(self, table: Any) -> Optional[str]:
        """Export table to markdown format."""
        try:
            # Method 1: Use built-in export
            if hasattr(table, 'export_to_markdown'):
                return table.export_to_markdown()
            
            # Method 2: Build markdown from rows
            if hasattr(table, 'rows') and table.rows:
                lines = []
                for row_idx, row in enumerate(table.rows):
                    cells = self._extract_row_data(row)
                    if isinstance(cells, list):
                        line = "| " + " | ".join(str(c) for c in cells) + " |"
                        lines.append(line)
                        
                        # Add header separator after first row
                        if row_idx == 0:
                            separator = "| " + " | ".join("---" for _ in cells) + " |"
                            lines.append(separator)
                
                return "\n".join(lines) if lines else None
            
            return None
            
        except Exception as e:
            logger.debug(f"Error exporting table to markdown: {e}")
            return None

    def _export_table_to_csv(self, table: Any) -> Optional[str]:
        """Export table to CSV format."""
        try:
            import csv
            from io import StringIO
            
            if not hasattr(table, 'rows') or not table.rows:
                return None
            
            output = StringIO()
            writer = csv.writer(output)
            
            for row in table.rows:
                cells = self._extract_row_data(row)
                if isinstance(cells, list):
                    writer.writerow(cells)
            
            csv_content = output.getvalue()
            return csv_content if csv_content else None
            
        except Exception as e:
            logger.debug(f"Error exporting table to CSV: {e}")
            return None

    def _save_summary(
        self,
        file_path: Path,
        result: Any,
        markdown_text: str,
        images_saved: int,
        tables_saved: int,
    ) -> None:
        """Save extraction summary with comprehensive statistics."""
        try:
            # Get page count
            pages_count = 0
            if hasattr(result, 'document') and hasattr(result.document, 'pages'):
                pages_count = len(result.document.pages)
            
            # Create output files description
            output_files = {
                "markdown": "markdown.md",
                "json": "document.json",
                "metadata": "metadata.json",
            }
            
            if images_saved > 0:
                output_files["images"] = f"images/ ({images_saved} files)"
            if tables_saved > 0:
                output_files["tables"] = f"tables/ ({tables_saved} files)"
            
            # Add source file info
            additional_stats = {}
            if hasattr(result, 'input') and hasattr(result.input, 'file'):
                additional_stats["source_file"] = str(result.input.file)
            
            # Create standardized summary
            summary = create_extraction_summary(
                library_name=self.library_name,
                markdown_text=markdown_text,
                images_count=images_saved,
                tables_count=tables_saved,
                pages_count=pages_count,
                additional_stats=additional_stats,
                output_files=output_files,
            )
            
            # Add Docling version
            summary["docling_version"] = get_library_version("docling")
            
            save_json_file(file_path, summary)
                
        except Exception as e:
            logger.error(f"Failed to save summary: {e}", exc_info=True)
