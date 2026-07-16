"""
Example usage of Docling extractor.

Demonstrates how to use the Docling adapter for comprehensive PDF extraction.
"""

from pathlib import Path
from app.extractors.docling_extractor import DoclingExtractor
from app.benchmark.benchmark_engine import BenchmarkEngine


def example_docling_basic():
    """Basic Docling extraction example."""
    print("=" * 70)
    print("Example 1: Basic Docling Extraction")
    print("=" * 70)
    
    extractor = DoclingExtractor()
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


def example_docling_with_benchmark():
    """Docling extraction with performance monitoring."""
    print("=" * 70)
    print("Example 2: Docling with Benchmark Engine")
    print("=" * 70)
    
    engine = BenchmarkEngine(sampling_interval_ms=50)
    extractor = DoclingExtractor()
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
            library_name="docling",
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


def example_docling_outputs():
    """Demonstrate Docling multiple output formats."""
    print("=" * 70)
    print("Example 3: Docling Multiple Output Formats")
    print("=" * 70)
    
    extractor = DoclingExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Extract with all outputs
        text = extractor.extract_text(pdf_path)
        
        print(f"✓ Extraction completed!")
        print(f"\nOutputs saved to: results/{{timestamp}}/docling/")
        print(f"  - markdown.md      : Markdown formatted text")
        print(f"  - document.json    : Complete document structure")
        print(f"  - metadata.json    : Document metadata")
        print(f"  - images/          : Extracted images")
        print(f"  - tables/          : Extracted tables (JSON + MD)")
        print(f"  - summary.json     : Extraction summary")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_docling_via_api():
    """Example API request for Docling extraction."""
    print("=" * 70)
    print("Example 4: API Request for Docling")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print("Content-Type: application/json")
    print()
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["docling"]')
    print('}')
    print()
    print("Response includes:")
    print('{')
    print('  "extraction_results": [{')
    print('    "library_name": "docling",')
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
    print("Plus all outputs saved to: results/{timestamp}/docling/")
    print()


def example_docling_comparison():
    """Example comparing Docling with other extractors."""
    print("=" * 70)
    print("Example 5: Docling vs Other Extractors")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["pypdf", "pdfplumber", "pymupdf", "docling"]')
    print('}')
    print()
    print("Docling advantages:")
    print("  ✓ Multiple output formats (Markdown, JSON)")
    print("  ✓ Image extraction")
    print("  ✓ Table extraction with structure")
    print("  ✓ Rich metadata")
    print("  ✓ Advanced document understanding")
    print()
    print("Trade-offs:")
    print("  - May be slower than PyMuPDF")
    print("  - Higher memory usage")
    print("  - More complex output handling")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DOCLING EXTRACTOR EXAMPLES" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Run examples
    example_docling_basic()
    example_docling_with_benchmark()
    example_docling_outputs()
    example_docling_via_api()
    example_docling_comparison()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nNote: Install Docling first: pip install docling")
