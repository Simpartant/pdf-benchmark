"""
Example usage of OpenDataLoader extractor.

Demonstrates how to use the OpenDataLoader adapter for PDF extraction.
"""

from pathlib import Path
from app.extractors.opendataloader_extractor import OpenDataLoaderExtractor
from app.benchmark.benchmark_engine import BenchmarkEngine


def example_opendataloader_basic():
    """Basic OpenDataLoader extraction example."""
    print("=" * 70)
    print("Example 1: Basic OpenDataLoader Extraction")
    print("=" * 70)
    
    extractor = OpenDataLoaderExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Extract text
        text = extractor.extract_text(pdf_path)
        
        print(f"✓ Extraction successful!")
        print(f"  Text length: {len(text)} characters")
        print(f"  First 200 chars: {text[:200]}...")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_opendataloader_with_benchmark():
    """OpenDataLoader extraction with performance monitoring."""
    print("=" * 70)
    print("Example 2: OpenDataLoader with Benchmark Engine")
    print("=" * 70)
    
    engine = BenchmarkEngine(sampling_interval_ms=50)
    extractor = OpenDataLoaderExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Run benchmarked extraction
        result = engine.run_extraction(
            extraction_func=extractor.extract_text,
            pdf_path=pdf_path,
            library_name="opendataloader",
        )
        
        print(f"✓ Benchmarked extraction completed!")
        print(f"  Success: {result.success}")
        print(f"  Execution time: {result.execution_time_ms:.2f}ms")
        print(f"  Memory usage: {result.memory_usage_mb:.2f}MB")
        print(f"  CPU usage: {result.cpu_usage_percent:.1f}%")
        print(f"  Characters: {result.char_count}")
        print(f"  Words: {result.word_count}")
        print(f"  Pages: {result.pages_extracted}")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_opendataloader_outputs():
    """Demonstrate OpenDataLoader output formats."""
    print("=" * 70)
    print("Example 3: OpenDataLoader Output Formats")
    print("=" * 70)
    
    extractor = OpenDataLoaderExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Extract with all outputs
        text = extractor.extract_text(pdf_path)
        
        print(f"✓ Extraction completed!")
        print(f"\nOutputs saved to: results/{{timestamp}}/opendataloader/")
        print(f"  - markdown.md      : Markdown formatted text")
        print(f"  - documents.json   : Structured documents")
        print(f"  - metadata.json    : Document metadata")
        print(f"  - images/          : Extracted images")
        print(f"  - tables/          : Extracted tables")
        print(f"  - summary.json     : Extraction summary")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_opendataloader_via_api():
    """Example API request for OpenDataLoader extraction."""
    print("=" * 70)
    print("Example 4: API Request for OpenDataLoader")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print("Content-Type: application/json")
    print()
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["opendataloader"]')
    print('}')
    print()
    print("Response includes:")
    print('{')
    print('  "extraction_results": [{')
    print('    "library_name": "opendataloader",')
    print('    "success": true,')
    print('    "execution_time_ms": 1234.56,')
    print('    "memory_usage_mb": 128.5,')
    print('    "cpu_usage_percent": 45.2,')
    print('    "text_content": "...markdown text...",')
    print('    "char_count": 5000,')
    print('    "word_count": 850')
    print('  }]')
    print('}')
    print()
    print("Plus all outputs saved to: results/{timestamp}/opendataloader/")
    print()


def example_opendataloader_comparison():
    """Example comparing all extractors including OpenDataLoader."""
    print("=" * 70)
    print("Example 5: Compare All Extractors")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": [')
    print('    "pypdf",')
    print('    "pdfplumber",')
    print('    "pymupdf",')
    print('    "docling",')
    print('    "mineru",')
    print('    "unstructured",')
    print('    "opendataloader"')
    print('  ]')
    print('}')
    print()
    print("OpenDataLoader features:")
    print("  ✓ Document-based extraction")
    print("  ✓ Unified data loading interface")
    print("  ✓ Metadata support")
    print("  ✓ Image and table extraction")
    print("  ✓ Multiple output formats")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 11 + "OPENDATALOADER EXTRACTOR EXAMPLES" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Run examples
    example_opendataloader_basic()
    example_opendataloader_with_benchmark()
    example_opendataloader_outputs()
    example_opendataloader_via_api()
    example_opendataloader_comparison()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nNote: Install OpenDataLoader first: pip install opendataloader")
