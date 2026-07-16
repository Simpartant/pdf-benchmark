"""Benchmark engine for running and measuring PDF extractions."""

import time
import json
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from uuid import uuid4

from loguru import logger

from app.benchmark.performance_monitor import PerformanceMonitor, PerformanceMetrics
from app.models.extraction_result import ExtractionResult
from app.utils.text_utils import count_words, count_characters
from app.core.config import settings


class BenchmarkEngine:
    """
    Engine for running benchmarked extractions with performance monitoring.
    
    Wraps any extraction function and measures:
    - Execution time
    - Peak memory usage
    - Average CPU usage
    """

    def __init__(self, sampling_interval_ms: float = 50):
        """
        Initialize benchmark engine.
        
        Args:
            sampling_interval_ms: Performance sampling interval in milliseconds
        """
        self.sampling_interval_ms = sampling_interval_ms

    def run_extraction(
        self,
        extraction_func: Callable[[Path], str],
        pdf_path: Path,
        library_name: str,
    ) -> ExtractionResult:
        """
        Run extraction with performance monitoring.
        
        Args:
            extraction_func: Function that extracts text from PDF
            pdf_path: Path to PDF file
            library_name: Name of extraction library
            
        Returns:
            ExtractionResult with performance metrics
        """
        logger.info(f"Starting benchmarked extraction with {library_name}")
        
        # Create performance monitor
        monitor = PerformanceMonitor(sampling_interval_ms=self.sampling_interval_ms)
        
        # Variables to capture results
        extracted_text = ""
        error_message: Optional[str] = None
        success = False
        
        try:
            # Start monitoring
            monitor.start()
            start_time = time.time()
            
            # Run extraction
            extracted_text = extraction_func(pdf_path)
            success = True
            
            # Stop monitoring
            end_time = time.time()
            metrics = monitor.stop()
            
            logger.info(
                f"Extraction completed successfully: {library_name}, "
                f"time={metrics.elapsed_time_ms:.2f}ms"
            )
            
        except Exception as e:
            # Stop monitoring on error
            metrics = monitor.stop()
            error_message = str(e)
            success = False
            logger.error(f"Extraction failed with {library_name}: {error_message}")
        
        # Calculate text statistics
        char_count = count_characters(extracted_text) if extracted_text else 0
        word_count = count_words(extracted_text) if extracted_text else 0
        
        # Count pages (basic heuristic - can be improved)
        pages_extracted = self._estimate_pages(extracted_text)
        
        # Collect comprehensive output metrics
        output_metrics = self._collect_output_metrics(library_name, extracted_text)
        
        # Create result with comprehensive metrics
        result = ExtractionResult(
            library_name=library_name,
            success=success,
            text_content=extracted_text,
            execution_time_ms=metrics.elapsed_time_ms,
            memory_usage_mb=metrics.peak_memory_mb,
            cpu_usage_percent=metrics.average_cpu_percent,
            pages_extracted=pages_extracted,
            char_count=char_count,
            word_count=word_count,
            error_message=error_message,
            # Comprehensive output metrics
            output_size_bytes=output_metrics['output_size_bytes'],
            images_count=output_metrics['images_count'],
            tables_count=output_metrics['tables_count'],
            markdown_length=output_metrics['markdown_length'],
            json_size_bytes=output_metrics['json_size_bytes'],
            output_directory=output_metrics['output_directory'],
            metadata={
                "sampling_interval_ms": self.sampling_interval_ms,
                "memory_samples_count": len(metrics.memory_samples),
                "cpu_samples_count": len(metrics.cpu_samples),
                "peak_memory_mb": metrics.peak_memory_mb,
                "average_cpu_percent": metrics.average_cpu_percent,
                **output_metrics.get('additional_metadata', {}),
            },
        )
        
        logger.info(
            f"Benchmark result: {library_name}, "
            f"success={success}, chars={char_count}, words={word_count}"
        )
        
        return result

    def _collect_output_metrics(self, library_name: str, extracted_text: str) -> Dict[str, Any]:
        """
        Collect comprehensive output metrics from extraction outputs.
        
        Scans the results directory for the latest output from this library
        and collects metrics about:
        - Total output size (all files)
        - Number of images
        - Number of tables
        - Markdown file length
        - JSON file size
        
        Args:
            library_name: Name of the extraction library
            extracted_text: Extracted text content
            
        Returns:
            Dictionary with output metrics
        """
        metrics = {
            'output_size_bytes': 0,
            'images_count': 0,
            'tables_count': 0,
            'markdown_length': len(extracted_text) if extracted_text else 0,
            'json_size_bytes': 0,
            'output_directory': None,
            'additional_metadata': {},
        }
        
        try:
            # Find the latest output directory for this library
            results_dir = Path(settings.results_dir)
            if not results_dir.exists():
                return metrics
            
            # Get all timestamped directories, sorted by most recent
            timestamp_dirs = sorted(
                [d for d in results_dir.iterdir() if d.is_dir()],
                key=lambda d: d.stat().st_mtime,
                reverse=True
            )
            
            # Look for the library's output directory in recent results
            output_dir = None
            for ts_dir in timestamp_dirs[:5]:  # Check last 5 results
                lib_dir = ts_dir / library_name
                if lib_dir.exists() and lib_dir.is_dir():
                    output_dir = lib_dir
                    break
            
            if not output_dir:
                logger.debug(f"No output directory found for {library_name}")
                return metrics
            
            metrics['output_directory'] = str(output_dir)
            
            # Calculate total output size
            total_size = 0
            for file in output_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
            
            metrics['output_size_bytes'] = total_size
            
            # Count images
            images_dir = output_dir / 'images'
            if images_dir.exists():
                image_files = list(images_dir.glob('*'))
                metrics['images_count'] = len([f for f in image_files if f.is_file()])
            
            # Count tables
            tables_dir = output_dir / 'tables'
            if tables_dir.exists():
                # Count JSON files (each table has JSON, MD, CSV - count unique tables)
                table_json_files = list(tables_dir.glob('*.json'))
                metrics['tables_count'] = len(table_json_files)
            
            # Get markdown file size
            markdown_file = output_dir / 'markdown.md'
            if markdown_file.exists():
                metrics['markdown_length'] = markdown_file.stat().st_size
            
            # Get JSON file size
            json_file = output_dir / 'document.json'
            if json_file.exists():
                metrics['json_size_bytes'] = json_file.stat().st_size
            
            # Load summary.json if available for additional metadata
            summary_file = output_dir / 'summary.json'
            if summary_file.exists():
                try:
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        summary_data = json.load(f)
                    
                    # Extract additional metrics from summary
                    if 'statistics' in summary_data:
                        stats = summary_data['statistics']
                        # Update with actual counts from summary if available
                        if 'images_extracted' in stats:
                            metrics['images_count'] = stats['images_extracted']
                        if 'tables_extracted' in stats:
                            metrics['tables_count'] = stats['tables_extracted']
                    
                    # Store full summary in additional metadata
                    metrics['additional_metadata']['summary'] = summary_data
                    
                except Exception as e:
                    logger.debug(f"Could not load summary.json: {e}")
            
            logger.debug(
                f"Collected metrics for {library_name}: "
                f"size={metrics['output_size_bytes']} bytes, "
                f"images={metrics['images_count']}, "
                f"tables={metrics['tables_count']}"
            )
            
        except Exception as e:
            logger.warning(f"Error collecting output metrics for {library_name}: {e}")
        
        return metrics

    def _estimate_pages(self, text: str) -> int:
        """
        Estimate number of pages from text.
        
        Basic heuristic: ~400 words per page or form feed characters.
        
        Args:
            text: Extracted text
            
        Returns:
            Estimated page count
        """
        if not text:
            return 0
        
        # Look for form feed characters (page breaks)
        form_feeds = text.count('\f')
        if form_feeds > 0:
            return form_feeds + 1
        
        # Estimate from word count
        word_count = count_words(text)
        estimated_pages = max(1, round(word_count / 400))
        
        return estimated_pages
