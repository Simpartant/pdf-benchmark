"""
Example usage of Unstructured extractor.

Demonstrates how to use the Unstructured adapter for comprehensive PDF extraction.
"""

from pathlib import Path
from app.extractors.unstructured_extractor import UnstructuredExtractor
from app.benchmark.benchmark_engine import BenchmarkEngine


def example_unstructured_basic():
    """Basic Unstructured extraction example."""
    print("=" * 70)
    print("Example 1: Basic Unstructured Extraction")
    print("=" * 70)
    
    extractor = UnstructuredExtractor()
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


def example_unstructured_with_benchmark():
    """Unstructured extraction with performance monitoring."""
    print("=" * 70)
    print("Example 2: Unstructured with Benchmark Engine")
    print("=" * 70)
    
    engine = BenchmarkEngine(sampling_interval_ms=50)
    extractor = UnstructuredExtractor()
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
            library_name="unstructured",
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


def example_unstructured_outputs():
    """Demonstrate Unstructured multiple output formats."""
    print("=" * 70)
    print("Example 3: Unstructured Multiple Output Formats")
    print("=" * 70)
    
    extractor = UnstructuredExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Extract with all outputs
        text = extractor.extract_text(pdf_path)
        
        print(f"✓ Extraction completed!")
        print(f"\nOutputs saved to: results/{{timestamp}}/unstructured/")
        print(f"  - markdown.md      : Markdown formatted text")
        print(f"  - elements.json    : Structured elements")
        print(f"  - metadata.json    : Document metadata")
        print(f"  - images/          : Extracted images")
        print(f"  - tables/          : Extracted tables (JSON + MD)")
        print(f"  - summary.json     : Extraction summary")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_unstructured_via_api():
    """Example API request for Unstructured extraction."""
    print("=" * 70)
    print("Example 4: API Request for Unstructured")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print("Content-Type: application/json")
    print()
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["unstructured"]')
    print('}')
    print()
    print("Response includes:")
    print('{')
    print('  "extraction_results": [{')
    print('    "library_name": "unstructured",')
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
    print("Plus all outputs saved to: results/{timestamp}/unstructured/")
    print()


def example_unstructured_comparison():
    """Example comparing Unstructured with other extractors."""
    print("=" * 70)
    print("Example 5: Unstructured vs Other Extractors")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["pypdf", "pdfplumber", "pymupdf", "docling", "mineru", "unstructured"]')
    print('}')
    print()
    print("Unstructured advantages:")
    print("  ✓ Element-based extraction")
    print("  ✓ High-resolution strategy")
    print("  ✓ Universal document processing")
    print("  ✓ Multiple output formats (Markdown, JSON)")
    print("  ✓ Image and table extraction")
    print("  ✓ Element type classification")
    print()
    print("Trade-offs:")
    print("  - May be slower than PyMuPDF")
    print("  - Higher memory usage")
    print("  - More dependencies")
    print()


def example_unstructured_features():
    """Demonstrate Unstructured unique features."""
    print("=" * 70)
    print("Example 6: Unstructured Unique Features")
    print("=" * 70)
    
    print("Element Types Detected:")
    print("  ✓ Title - Document titles and headings")
    print("  ✓ NarrativeText - Body text paragraphs")
    print("  ✓ ListItem - Bulleted/numbered list items")
    print("  ✓ Table - Structured tables with HTML")
    print("  ✓ Image - Images with base64 data")
    print("  ✓ PageBreak - Page boundaries")
    print()
    print("Extraction Strategy:")
    print("  ✓ hi_res - High resolution for best quality")
    print("  ✓ extract_images_in_pdf - Extract images")
    print("  ✓ infer_table_structure - Detect table structure")
    print("  ✓ include_page_breaks - Track page boundaries")
    print()
    print("Output Formats:")
    print("  ✓ Markdown with proper formatting")
    print("  ✓ JSON with element classification")
    print("  ✓ Metadata with element type counts")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 13 + "UNSTRUCTURED EXTRACTOR EXAMPLES" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Run examples
    example_unstructured_basic()
    example_unstructured_with_benchmark()
    example_unstructured_outputs()
    example_unstructured_via_api()
    example_unstructured_comparison()
    example_unstructured_features()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nNote: Install Unstructured first: pip install unstructured[pdf]")
