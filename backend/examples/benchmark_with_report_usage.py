"""
Example: Automatic Benchmark Report Generation

This example demonstrates how to run a PDF extraction benchmark
and automatically generate a comprehensive markdown report.
"""

from pathlib import Path
from app.services.extraction_service import ExtractionService
from loguru import logger


def main():
    """Run benchmark with automatic report generation."""
    
    # Configure logger
    logger.add("logs/benchmark_report_{time}.log", rotation="1 day")
    
    # Initialize service
    service = ExtractionService()
    
    # PDF file to benchmark
    pdf_path = Path("data/sample.pdf")
    
    # Libraries to test
    libraries = [
        "pypdf",
        "pdfplumber", 
        "pymupdf",
        "docling",
        "mineru",
        "unstructured",
        "opendataloader"
    ]
    
    # Output directory
    output_dir = Path("results")
    
    # Run benchmark and generate report
    logger.info("Starting benchmark with report generation")
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Libraries: {', '.join(libraries)}")
    
    results, report_path = service.run_benchmark_with_report(
        pdf_path=pdf_path,
        library_names=libraries,
        output_dir=output_dir,
    )
    
    # Display summary
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)
    print(f"\nTotal libraries tested: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r.success)}")
    print(f"Failed: {sum(1 for r in results if not r.success)}")
    print(f"\nReport generated: {report_path}")
    print("\nResults summary:")
    
    for result in results:
        status = "✅" if result.success else "❌"
        time_str = f"{result.execution_time_ms:.2f}ms" if result.success else "N/A"
        memory_str = f"{result.peak_memory_mb:.2f}MB" if result.success else "N/A"
        print(f"  {status} {result.library_name:20s} - {time_str:12s} {memory_str:12s}")
    
    print(f"\n📄 Full report: {report_path.absolute()}")
    print("="*60)


if __name__ == "__main__":
    main()
