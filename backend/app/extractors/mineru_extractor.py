"""MinerU extractor implementation."""

import json
from pathlib import Path
from typing import Any
from datetime import datetime

from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    create_timestamped_output_directory,
    save_text_file,
    save_json_file,
    get_library_version,
    count_images_in_directory,
    create_extraction_summary,
)


class MinerUExtractor(BaseExtractor):
    """
    MinerU PDF extraction implementation.
    
    Extracts PDF content to multiple formats:
    - Markdown text
    - JSON structure
    - Images
    - Tables
    - Metadata
    
    Saves all outputs to results/{timestamp}/mineru/
    """

    def __init__(self):
        super().__init__("mineru")
        self._mineru_available = self._check_mineru_installation()

    def _check_mineru_installation(self) -> bool:
        """Check if MinerU is installed."""
        try:
            import magic_pdf
            try:
                from importlib.metadata import version
                mineru_version = version("magic-pdf")
                logger.info(f"MinerU available: version {mineru_version}")
            except Exception:
                logger.info("MinerU available (version unknown)")
            return True
        except ImportError:
            logger.warning("MinerU not installed")
            return False

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract PDF with MinerU (legacy method).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._mineru_available:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="MinerU is not installed. Install with: pip install magic-pdf[full]",
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
            logger.error(f"MinerU extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
            )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text using MinerU with full feature support.
        
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
            ImportError: If MinerU not installed
            Exception: For extraction errors
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._mineru_available:
            raise ImportError("MinerU is not installed. Install with: pip install magic-pdf[full]")

        try:
            # Import MinerU components
            from magic_pdf.pipe.UNIPipe import UNIPipe
            from magic_pdf.pipe.OCRPipe import OCRPipe
            from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
            import magic_pdf.model as model_config
            
            logger.info(f"Starting MinerU extraction for {pdf_path}")
            start_time = datetime.now()
            
            # Create output directory
            output_dir = create_timestamped_output_directory(self.library_name, pdf_path)
            logger.info(f"MinerU output directory: {output_dir}")
            
            # Read PDF bytes
            pdf_bytes = pdf_path.read_bytes()
            
            # Create reader/writer
            image_writer = DiskReaderWriter(str(output_dir))
            
            # Try with layout analysis first
            try:
                # Initialize pipe with auto mode (tries to detect best method)
                # MinerU API: UNIPipe(pdf_bytes, image_writer)
                pipe = UNIPipe(pdf_bytes, image_writer)
                
                # Classify document type
                pipe.pipe_classify()
                
                # Parse document
                pipe.pipe_parse()
                
                # Get content in different formats
                markdown_text = pipe.pipe_mk_markdown(
                    str(output_dir),
                    drop_mode="none"
                )
                
                # Get structured content
                content_list = pipe.pipe_mk_uni_format(str(output_dir), drop_mode="none")
                
            except Exception as e:
                logger.warning(f"UNIPipe failed, trying OCR mode: {e}")
                # Fallback to OCR if layout analysis fails
                pipe = OCRPipe(pdf_bytes, image_writer)
                pipe.pipe_classify()
                pipe.pipe_parse()
                markdown_text = pipe.pipe_mk_markdown(
                    str(output_dir),
                    drop_mode="none"
                )
                content_list = pipe.pipe_mk_uni_format(str(output_dir), drop_mode="none")
            
            # Save outputs
            self._save_outputs(
                output_dir=output_dir,
                pipe=pipe,
                markdown_text=markdown_text,
                content_list=content_list,
            )
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"MinerU extraction completed in {extraction_time:.2f}s: "
                f"{len(markdown_text)} characters, outputs saved to {output_dir}"
            )
            
            return markdown_text
            
        except ImportError as e:
            logger.error(f"MinerU import error: {e}")
            raise ImportError(f"Failed to import MinerU: {e}")
            
        except Exception as e:
            logger.error(f"MinerU extraction failed: {e}", exc_info=True)
            raise Exception(f"MinerU extraction error: {e}")

    def _save_outputs(
        self,
        output_dir: Path,
        pipe: Any,
        markdown_text: str,
        content_list: list,
    ) -> None:
        """
        Save all MinerU outputs to directory.
        
        Saves:
        - markdown.md: Markdown text
        - content.json: Structured content
        - metadata.json: Document metadata
        - images/: Extracted images (auto-saved by MinerU)
        - tables/: Extracted tables (from content)
        
        Args:
            output_dir: Output directory path
            pipe: MinerU pipe instance
            markdown_text: Markdown text content
            content_list: Structured content list
        """
        try:
            # Save markdown
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            logger.debug(f"Saved markdown: {markdown_file}")
            
            # Save structured content as JSON
            content_file = output_dir / "content.json"
            save_json_file(content_file, content_list)
            logger.debug(f"Saved content JSON: {content_file}")
            
            # Save metadata
            metadata_file = output_dir / "metadata.json"
            self._save_metadata(metadata_file, pipe, markdown_text)
            logger.debug(f"Saved metadata: {metadata_file}")
            
            # Extract and save tables from content
            tables_dir = output_dir / "tables"
            tables_saved = self._save_tables(tables_dir, content_list)
            if tables_saved:
                logger.debug(f"Saved {tables_saved} tables to: {tables_dir}")
            
            # Count images (MinerU saves them automatically)
            images_dir = output_dir / "images"
            images_saved = count_images_in_directory(images_dir)
            if images_saved:
                logger.debug(f"Found {images_saved} images in: {images_dir}")
            
            # Create summary file
            summary_file = output_dir / "summary.json"
            self._save_summary(summary_file, pipe, markdown_text, images_saved, tables_saved)
            logger.debug(f"Saved summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving MinerU outputs: {e}")
            # Don't raise - extraction succeeded even if save failed

    def _save_metadata(self, file_path: Path, pipe: Any, markdown_text: str) -> None:
        """Save document metadata."""
        try:
            metadata = {
                "extractor": self.library_name,
                "extraction_time": datetime.now().isoformat(),
                "mineru_version": get_library_version("magic_pdf"),
                "text_length": len(markdown_text),
                "word_count": len(markdown_text.split()),
            }
            
            # Add pipe metadata if available
            if hasattr(pipe, "pdf_mid_data"):
                metadata["pdf_info"] = {
                    "page_count": len(pipe.pdf_mid_data.get("pdf_info", [])),
                }
            
            save_json_file(file_path, metadata)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}", exc_info=True)

    def _save_tables(self, tables_dir: Path, content_list: list) -> int:
        """
        Extract and save tables from content list.
        
        Args:
            tables_dir: Directory to save tables
            content_list: Structured content list
            
        Returns:
            Number of tables saved
        """
        try:
            tables_dir.mkdir(parents=True, exist_ok=True)
            tables_saved = 0
            
            # Extract tables from content list
            for item in content_list:
                if isinstance(item, dict) and item.get("type") == "table":
                    try:
                        # Save table as JSON
                        json_file = tables_dir / f"table_{tables_saved:03d}.json"
                        save_json_file(json_file, item)
                        
                        # Save table as markdown if available
                        if "markdown" in item or "text" in item:
                            md_file = tables_dir / f"table_{tables_saved:03d}.md"
                            table_text = item.get("markdown", item.get("text", ""))
                            save_text_file(md_file, table_text)
                        
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
        pipe: Any,
        markdown_text: str,
        images_saved: int,
        tables_saved: int,
    ) -> None:
        """Save extraction summary."""
        try:
            # Get page count
            pages_count = 0
            if hasattr(pipe, "pdf_mid_data"):
                pages_count = len(pipe.pdf_mid_data.get("pdf_info", []))
            
            # Create standardized summary
            output_files = {
                "markdown": "markdown.md",
                "content": "content.json",
                "metadata": "metadata.json",
            }
            
            if images_saved > 0:
                output_files["images"] = f"images/ ({images_saved} files)"
            if tables_saved > 0:
                output_files["tables"] = f"tables/ ({tables_saved} files)"
            
            summary = create_extraction_summary(
                library_name=self.library_name,
                markdown_text=markdown_text,
                images_count=images_saved,
                tables_count=tables_saved,
                pages_count=pages_count,
                output_files=output_files,
            )
            
            save_json_file(file_path, summary)
                
        except Exception as e:
            logger.error(f"Failed to save summary: {e}", exc_info=True)