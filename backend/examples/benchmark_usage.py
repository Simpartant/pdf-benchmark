"""
Example usage of the Benchmark Engine.

This script demonstrates how to use the benchmark engine
for performance monitoring of PDF extractions.
"""

from pathlib import Path
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.benchmark.performance_monitor import PerformanceMonitor
from app.benchmark.result_storage import ResultStorageService
from app.extractors.pypdf_extractor import PyPDFExtractor


def example_1_performance_monitor():
    """Example: Using PerformanceMonitor directly."""
    print("=" * 60)
    print("Example 1: Performance Monitor")
    print("=" * 60)
    
    # Create monitor
    monitor = PerformanceMonitor(sampling_interval_ms=50)
    
    # Start monitoring
    monitor.start()
    
    # Simulate work
    import time
    time.sleep(0.5)
    
    # Stop and get metrics
    metrics = monitor.stop()
    
    print(f"Elapsed Time: {metrics.elapsed_time_ms:.2f}ms")
    print(f"Peak Memory: {metrics.peak_memory_mb:.2f}MB")
    print(f"Average CPU: {metrics.average_cpu_percent:.1f}%")
    print(f"Samples collected: {len(metrics.memory_samples)} memory, {len(metrics.cpu_samples)} CPU")
    print()


def example_2_context_manager():
    """Example: Using PerformanceMonitor as context manager."""
    print("=" * 60)
    print("Example 2: Context Manager")
    print("=" * 60)
    
    with PerformanceMonitor(sampling_interval_ms=50) as monitor:
        # Do work
        import time
        time.sleep(0.3)
    
    # Get metrics after context exits
    metrics = monitor.stop()
    print(f"Elapsed Time: {metrics.elapsed_time_ms:.2f}ms")
    print(f"Peak Memory: {metrics.peak_memory_mb:.2f}MB")
    print()


def example_3_benchmark_engine():
    """Example: Using BenchmarkEngine for extraction."""
    print("=" * 60)
    print("Example 3: Benchmark Engine")
    print("=" * 60)
    
    # Create engine
    engine = BenchmarkEngine(sampling_interval_ms=50)
    
    # Create extractor
    extractor = PyPDFExtractor()
    
    # Example extraction function
    def sample_extraction(pdf_path: Path) -> str:
        """Simulate extraction that returns text."""
        import time
        time.sleep(0.2)  # Simulate work
        return "Sample extracted text from PDF document."
    
    # Run benchmarked extraction
    result = engine.run_extraction(
        extraction_func=sample_extraction,
        pdf_path=Path("sample.pdf"),
        library_name="pypdf",
    )
    
    print(f"Success: {result.success}")
    print(f"Library: {result.library_name}")
    print(f"Execution Time: {result.execution_time_ms:.2f}ms")
    print(f"Memory Usage: {result.memory_usage_mb:.2f}MB")
    print(f"CPU Usage: {result.cpu_usage_percent:.1f}%")
    print(f"Characters: {result.char_count}")
    print(f"Words: {result.word_count}")
    print(f"Pages: {result.pages_extracted}")
    print()


def example_4_result_storage():
    """Example: Storing benchmark results."""
    print("=" * 60)
    print("Example 4: Result Storage")
    print("=" * 60)
    
    from app.models.benchmark_result import BenchmarkResult
    from app.models.extraction_result import ExtractionResult
    from uuid import uuid4
    from datetime import datetime
    
    # Create sample results
    results = [
        ExtractionResult(
            library_name="pypdf",
            success=True,
            text_content="Sample text",
            execution_time_ms=123.45,
            memory_usage_mb=45.2,
            cpu_usage_percent=25.5,
            pages_extracted=5,
            char_count=100,
            word_count=20,
        ),
        ExtractionResult(
            library_name="pdfplumber",
            success=True,
            text_content="Sample text",
            execution_time_ms=156.78,
            memory_usage_mb=62.8,
            cpu_usage_percent=30.2,
            pages_extracted=5,
            char_count=105,
            word_count=21,
        ),
    ]
    
    # Create benchmark result
    benchmark = BenchmarkResult(
        pdf_filename="sample.pdf",
        pdf_id=uuid4(),
        extraction_results=results,
    )
    benchmark.calculate_summary()
    
    # Store to disk
    storage = ResultStorageService()
    result_dir = storage.store_benchmark_result(benchmark)
    
    print(f"Results stored to: {result_dir}")
    print(f"Files created:")
    print(f"  - benchmark.json")
    print(f"  - metadata.json")
    print(f"  - extraction_pypdf.json")
    print(f"  - extraction_pdfplumber.json")
    print()
    
    # List all stored results
    all_results = storage.list_stored_results()
    print(f"Total stored results: {len(all_results)}")
    print()


def example_5_full_workflow():
    """Example: Complete workflow from extraction to storage."""
    print("=" * 60)
    print("Example 5: Full Workflow")
    print("=" * 60)
    
    from app.services.extraction_service import ExtractionService
    from app.benchmark.benchmark_service import BenchmarkService
    from app.services.history_service import HistoryService
    from app.models.document import PDFDocument
    from uuid import uuid4
    
    # Create services
    extraction_service = ExtractionService()
    history_service = HistoryService()
    result_storage = ResultStorageService()
    
    benchmark_service = BenchmarkService(
        extraction_service=extraction_service,
        history_service=history_service,
        result_storage=result_storage,
    )
    
    # Create PDF document
    pdf_doc = PDFDocument(
        filename="sample.pdf",
        file_path="./sample-pdfs/sample.pdf",
        size_bytes=102400,
    )
    
    # Run benchmark (Note: Will fail as extraction not implemented)
    try:
        result = benchmark_service.run_benchmark(
            pdf_document=pdf_doc,
            library_names=["pypdf", "pdfplumber", "pymupdf"],
        )
        
        print(f"Benchmark ID: {result.id}")
        print(f"Total Duration: {result.total_duration_ms:.2f}ms")
        print(f"Fastest Library: {result.fastest_library}")
        print(f"Most Efficient: {result.most_efficient_memory}")
        print()
        
    except Exception as e:
        print(f"Note: Extraction not yet implemented")
        print(f"Error: {e}")
        print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "BENCHMARK ENGINE EXAMPLES" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    # Run examples
    example_1_performance_monitor()
    example_2_context_manager()
    example_3_benchmark_engine()
    example_4_result_storage()
    example_5_full_workflow()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
