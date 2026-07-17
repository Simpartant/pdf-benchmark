"""Extraction service for coordinating PDF extractions."""

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.extractors.base_extractor import BaseExtractor
from app.extractors.pypdf_extractor import PyPDFExtractor
from app.extractors.pdfplumber_extractor import PDFPlumberExtractor
from app.extractors.pymupdf_extractor import PyMuPDFExtractor
from app.extractors.docling_extractor import DoclingExtractor
from app.extractors.mineru_extractor import MinerUExtractor
from app.extractors.unstructured_extractor import UnstructuredExtractor
from app.models.extraction_result import ExtractionResult
from app.models.document import PDFDocument
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.services.report_service import ReportService
from loguru import logger


class ExtractionService:
    """Service for managing PDF extraction operations with benchmarking."""

    def __init__(self, benchmark_engine: Optional[BenchmarkEngine] = None):
        """
        Initialize extraction service with available extractors.
        
        Args:
            benchmark_engine: Optional BenchmarkEngine for performance monitoring
        """
        self._extractors: dict[str, BaseExtractor] = {
            "pypdf": PyPDFExtractor(),
            "pdfplumber": PDFPlumberExtractor(),
            "pymupdf": PyMuPDFExtractor(),
            "docling": DoclingExtractor(),
            "mineru": MinerUExtractor(),
            "unstructured": UnstructuredExtractor(),
        }
        self.benchmark_engine = benchmark_engine or BenchmarkEngine()
        self.report_service = ReportService()

    def get_extractor(self, library_name: str) -> Optional[BaseExtractor]:
        """
        Get extractor by library name.
        
        Args:
            library_name: Name of the extraction library
            
        Returns:
            BaseExtractor instance or None
        """
        return self._extractors.get(library_name)

    def extract_with_library(
        self,
        pdf_path: Path,
        library_name: str,
    ) -> ExtractionResult:
        """
        Extract text from PDF using specified library with benchmarking.
        
        Args:
            pdf_path: Path to PDF file
            library_name: Name of library to use
            
        Returns:
            ExtractionResult with extraction data and performance metrics
            
        Raises:
            ValueError: If library not found
        """
        extractor = self.get_extractor(library_name)
        if extractor is None:
            logger.error(f"Unknown extraction library: {library_name}")
            return ExtractionResult(
                library_name=library_name,
                success=False,
                error_message=f"Unknown extraction library: {library_name}",
            )

        try:
            logger.info(f"Starting benchmarked extraction with {library_name} for {pdf_path}")
            
            # Use benchmark engine to run extraction with performance monitoring
            result = self.benchmark_engine.run_extraction(
                extraction_func=extractor.extract_text,  # Use the new method
                pdf_path=pdf_path,
                library_name=library_name,
            )
            
            logger.info(
                f"Extraction completed: {library_name}, "
                f"success={result.success}, "
                f"chars={result.char_count}, "
                f"time={result.execution_time_ms:.2f}ms"
            )
            return result
        except Exception as e:
            logger.error(f"Extraction failed with {library_name}: {str(e)}")
            return ExtractionResult(
                library_name=library_name,
                success=False,
                error_message=str(e),
            )

    def extract_with_multiple_libraries(
        self,
        pdf_path: Path,
        library_names: List[str],
    ) -> List[ExtractionResult]:
        """
        Extract text using multiple libraries.
        
        Args:
            pdf_path: Path to PDF file
            library_names: List of library names to use
            
        Returns:
            List of ExtractionResult objects
        """
        results = []
        for library_name in library_names:
            result = self.extract_with_library(pdf_path, library_name)
            results.append(result)
        return results

    def get_available_extractors(self) -> List[str]:
        """
        Get list of available extractor names.
        
        Returns:
            List of library names
        """
        return list(self._extractors.keys())

    def run_benchmark_with_report(
        self,
        pdf_path: Path,
        library_names: List[str],
        output_dir: Path,
    ) -> tuple[List[ExtractionResult], Path]:
        """
        Run benchmark extractions and generate comprehensive report.
        
        Args:
            pdf_path: Path to PDF file
            library_names: List of library names to benchmark
            output_dir: Directory to save results and report
            
        Returns:
            Tuple of (extraction results, report path)
        """
        import os
        from datetime import datetime
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        results_dir = output_dir / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting benchmark with report for {len(library_names)} libraries")
        
        # Run extractions
        results = self.extract_with_multiple_libraries(pdf_path, library_names)
        
        # Get PDF info
        pdf_info = {
            "name": pdf_path.name,
            "size": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "pages": self._get_pdf_page_count(pdf_path),
        }
        
        # Convert results to dictionary format for report
        benchmark_results = {}
        for result in results:
            benchmark_results[result.library_name] = {
                "status": "success" if result.success else "failed",
                "execution_time_ms": result.execution_time_ms,
                "peak_memory_mb": result.peak_memory_mb,
                "avg_cpu_percent": result.avg_cpu_percent,
                "outputs": {
                    "markdown_size": len(result.markdown_text) if result.markdown_text else 0,
                    "json_size": len(result.metadata) if result.metadata else 0,
                    "images_count": len(result.images) if result.images else 0,
                    "tables_count": len(result.tables) if result.tables else 0,
                },
                "error": result.error_message if not result.success else None,
            }
        
        # Generate report
        logger.info("Generating benchmark report")
        report_path = self.report_service.generate_report(
            benchmark_results=benchmark_results,
            pdf_info=pdf_info,
            output_dir=results_dir,
        )
        
        logger.info(f"Benchmark report generated: {report_path}")
        
        return results, report_path
    
    def _get_pdf_page_count(self, pdf_path: Path) -> int:
        """
        Get page count from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages or 0 if unable to determine
        """
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            logger.warning(f"Could not determine PDF page count: {e}")
            return 0
