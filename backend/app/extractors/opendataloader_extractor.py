"""OpenDataLoader extractor implementation."""

import json
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


class OpenDataLoaderExtractor(BaseExtractor):
    """
    OpenDataLoader PDF extraction implementation.
    
    Extracts PDF content to multiple formats:
    - Markdown text
    - JSON structure
    - Images
    - Tables
    - Metadata
    
    Saves all outputs to results/{timestamp}/opendataloader/
    """

    def __init__(self):
        super().__init__("opendataloader")
        self._opendataloader_available = self._check_opendataloader_installation()

    def _check_opendataloader_installation(self) -> bool:
        """Check if OpenDataLoader is installed."""
        try:
            import opendataloader
            logger.info(f"OpenDataLoader available: version {opendataloader.__version__}")
            return True
        except ImportError:
            logger.warning("OpenDataLoader not installed")
            return False

    def extract(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract PDF with OpenDataLoader (legacy method).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with extracted data
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._opendataloader_available:
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message="OpenDataLoader is not installed. Install with: pip install opendataloader",
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
            logger.error(f"OpenDataLoader extraction failed: {e}")
            return ExtractionResult(
                library_name=self.library_name,
                success=False,
                error_message=str(e),
            )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text using OpenDataLoader with full feature support.
        
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
            ImportError: If OpenDataLoader not installed
            Exception: For extraction errors
        """
        # Validate PDF
        self.validate_pdf(pdf_path)
        
        if not self._opendataloader_available:
            raise ImportError("OpenDataLoader is not installed. Install with: pip install opendataloader")

        try:
            # Import OpenDataLoader components
            from opendataloader import PDFLoader
            
            logger.info(f"Starting OpenDataLoader extraction for {pdf_path}")
            start_time = datetime.now()
            
            # Create output directory
            output_dir = create_timestamped_output_directory(self.library_name, pdf_path)
            logger.info(f"OpenDataLoader output directory: {output_dir}")
            
            # Initialize loader
            loader = PDFLoader(
                file_path=str(pdf_path),
                extract_images=True,
                extract_tables=True,
            )
            
            # Load and parse document
            documents = loader.load()
            
            if not documents:
                raise Exception("No documents extracted from PDF")
            
            # Combine all document content
            markdown_text = self._documents_to_markdown(documents)
            json_structure = self._documents_to_dict(documents)
            
            # Save outputs
            self._save_outputs(
                output_dir=output_dir,
                documents=documents,
                markdown_text=markdown_text,
                json_structure=json_structure,
            )
            
            extraction_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"OpenDataLoader extraction completed in {extraction_time:.2f}s: "
                f"{len(markdown_text)} characters, outputs saved to {output_dir}"
            )
            
            return markdown_text
            
        except ImportError as e:
            logger.error(f"OpenDataLoader import error: {e}")
            raise ImportError(f"Failed to import OpenDataLoader: {e}")
            
        except Exception as e:
            logger.error(f"OpenDataLoader extraction failed: {e}", exc_info=True)
            raise Exception(f"OpenDataLoader extraction error: {e}")

    def _documents_to_markdown(self, documents: list) -> str:
        """
        Convert OpenDataLoader documents to markdown format.
        
        Args:
            documents: List of OpenDataLoader documents
            
        Returns:
            Markdown formatted text
        """
        markdown_lines = []
        
        for doc in documents:
            # Get page content
            page_content = doc.page_content if hasattr(doc, "page_content") else str(doc)
            markdown_lines.append(page_content)
            
            # Add metadata if available
            if hasattr(doc, "metadata") and doc.metadata:
                metadata = doc.metadata
                if metadata.get("page"):
                    markdown_lines.append(f"\n*[Page {metadata['page']}]*\n")
        
        return "\n\n".join(markdown_lines)

    def _documents_to_dict(self, documents: list) -> List[Dict[str, Any]]:
        """
        Convert OpenDataLoader documents to dictionary format.
        
        Args:
            documents: List of OpenDataLoader documents
            
        Returns:
            List of document dictionaries
        """
        result = []
        
        for idx, doc in enumerate(documents):
            doc_dict = {
                "index": idx,
                "content": doc.page_content if hasattr(doc, "page_content") else str(doc),
                "metadata": {}
            }
            
            # Add metadata if available
            if hasattr(doc, "metadata"):
                doc_dict["metadata"] = doc.metadata
            
            result.append(doc_dict)
        
        return result

    def _save_outputs(
        self,
        output_dir: Path,
        documents: list,
        markdown_text: str,
        json_structure: List[Dict[str, Any]],
    ) -> None:
        """
        Save all OpenDataLoader outputs to directory.
        
        Saves:
        - markdown.md: Markdown text
        - documents.json: Structured documents
        - metadata.json: Document metadata
        - images/: Extracted images (if available)
        - tables/: Extracted tables (if available)
        
        Args:
            output_dir: Output directory path
            documents: List of OpenDataLoader documents
            markdown_text: Markdown text content
            json_structure: Structured JSON data
        """
        try:
            # Save markdown
            markdown_file = output_dir / "markdown.md"
            save_text_file(markdown_file, markdown_text)
            logger.debug(f"Saved markdown: {markdown_file}")
            
            # Save JSON structure
            json_file = output_dir / "documents.json"
            save_json_file(json_file, json_structure)
            logger.debug(f"Saved documents JSON: {json_file}")
            
            # Save metadata
            metadata_file = output_dir / "metadata.json"
            self._save_metadata(metadata_file, documents, markdown_text)
            logger.debug(f"Saved metadata: {metadata_file}")
            
            # Extract and save images (if available in metadata)
            images_dir = output_dir / "images"
            images_saved = self._save_images(images_dir, documents)
            if images_saved:
                logger.debug(f"Saved {images_saved} images to: {images_dir}")
            
            # Extract and save tables (if available in metadata)
            tables_dir = output_dir / "tables"
            tables_saved = self._save_tables(tables_dir, documents)
            if tables_saved:
                logger.debug(f"Saved {tables_saved} tables to: {tables_dir}")
            
            # Create summary file
            summary_file = output_dir / "summary.json"
            self._save_summary(summary_file, documents, markdown_text, images_saved, tables_saved)
            logger.debug(f"Saved summary: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving OpenDataLoader outputs: {e}")
            # Don't raise - extraction succeeded even if save failed

    def _save_metadata(self, file_path: Path, documents: list, markdown_text: str) -> None:
        """Save document metadata."""
        try:
            # Extract pages from documents
            pages = set()
            for doc in documents:
                if hasattr(doc, "metadata") and doc.metadata.get("page"):
                    pages.add(doc.metadata["page"])
            
            metadata = {
                "extractor": self.library_name,
                "extraction_time": datetime.now().isoformat(),
                "opendataloader_version": get_library_version("opendataloader"),
                "total_documents": len(documents),
                "text_length": len(markdown_text),
                "word_count": len(markdown_text.split()),
                "pages": len(pages) if pages else 0,
            }
            
            save_json_file(file_path, metadata)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}", exc_info=True)

    def _save_images(self, images_dir: Path, documents: list) -> int:
        """
        Extract and save images from documents.
        
        Args:
            images_dir: Directory to save images
            documents: List of OpenDataLoader documents
            
        Returns:
            Number of images saved
        """
        try:
            images_dir.mkdir(parents=True, exist_ok=True)
            images_saved = 0
            
            for doc in documents:
                if hasattr(doc, "metadata") and doc.metadata:
                    metadata = doc.metadata
                    
                    # Check for images in metadata
                    if "images" in metadata and metadata["images"]:
                        for img_data in metadata["images"]:
                            try:
                                image_file = images_dir / f"image_{images_saved:03d}.png"
                                
                                # Save image if data available
                                if isinstance(img_data, bytes):
                                    with open(image_file, "wb") as f:
                                        f.write(img_data)
                                    images_saved += 1
                                    
                            except Exception as e:
                                logger.warning(f"Failed to save image {images_saved}: {e}")
            
            return images_saved
            
        except Exception as e:
            logger.error(f"Error saving images: {e}")
            return 0

    def _save_tables(self, tables_dir: Path, documents: list) -> int:
        """
        Extract and save tables from documents.
        
        Args:
            tables_dir: Directory to save tables
            documents: List of OpenDataLoader documents
            
        Returns:
            Number of tables saved
        """
        try:
            tables_dir.mkdir(parents=True, exist_ok=True)
            tables_saved = 0
            
            for doc in documents:
                if hasattr(doc, "metadata") and doc.metadata:
                    metadata = doc.metadata
                    
                    # Check for tables in metadata
                    if "tables" in metadata and metadata["tables"]:
                        for table_data in metadata["tables"]:
                            try:
                                # Save table as JSON
                                json_file = tables_dir / f"table_{tables_saved:03d}.json"
                                save_json_file(json_file, table_data)
                                
                                # Save table as markdown if text available
                                if isinstance(table_data, dict) and "text" in table_data:
                                    md_file = tables_dir / f"table_{tables_saved:03d}.md"
                                    save_text_file(md_file, table_data["text"])
                                
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
        documents: list,
        markdown_text: str,
        images_saved: int,
        tables_saved: int,
    ) -> None:
        """Save extraction summary."""
        try:
            # Count pages
            pages = set()
            for doc in documents:
                if hasattr(doc, "metadata") and doc.metadata.get("page"):
                    pages.add(doc.metadata["page"])
            
            # Create output files description
            output_files = {
                "markdown": "markdown.md",
                "documents": "documents.json",
                "metadata": "metadata.json",
            }
            
            if images_saved > 0:
                output_files["images"] = f"images/ ({images_saved} files)"
            if tables_saved > 0:
                output_files["tables"] = f"tables/ ({tables_saved} files)"
            
            # Additional statistics
            additional_stats = {
                "total_documents": len(documents),
            }
            
            # Create standardized summary
            summary = create_extraction_summary(
                library_name=self.library_name,
                markdown_text=markdown_text,
                images_count=images_saved,
                tables_count=tables_saved,
                pages_count=len(pages) if pages else 0,
                additional_stats=additional_stats,
                output_files=output_files,
            )
            
            # Add OpenDataLoader version
            summary["opendataloader_version"] = get_library_version("opendataloader")
            
            save_json_file(file_path, summary)
                
        except Exception as e:
            logger.error(f"Failed to save summary: {e}", exc_info=True)
