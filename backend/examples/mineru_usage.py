"""
Example usage of MinerU extractor.

Demonstrates how to use the MinerU adapter for comprehensive PDF extraction.
"""

from pathlib import Path
from app.extractors.mineru_extractor import MinerUExtractor
from app.benchmark.benchmark_engine import BenchmarkEngine


def example_mineru_basic():
    """Basic MinerU extraction example."""
    print("=" * 70)
    print("Example 1: Basic MinerU Extraction")
    print("=" * 70)
    
    extractor = MinerUExtractor()
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


def example_mineru_with_benchmark():
    """MinerU extraction with performance monitoring."""
    print("=" * 70)
    print("Example 2: MinerU with Benchmark Engine")
    print("=" * 70)
    
    engine = BenchmarkEngine(sampling_interval_ms=50)
    extractor = MinerUExtractor()
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
            library_name="mineru",
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


def example_mineru_outputs():
    """Demonstrate MinerU multiple output formats."""
    print("=" * 70)
    print("Example 3: MinerU Multiple Output Formats")
    print("=" * 70)
    
    extractor = MinerUExtractor()
    pdf_path = Path("./sample-pdfs/test.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("Please create a sample PDF file first.")
        return
    
    try:
        # Extract with all outputs
        text = extractor.extract_text(pdf_path)
        
        print(f"✓ Extraction completed!")
        print(f"\nOutputs saved to: results/{{timestamp}}/mineru/")
        print(f"  - markdown.md      : Markdown formatted text")
        print(f"  - content.json     : Structured content")
        print(f"  - metadata.json    : Document metadata")
        print(f"  - images/          : Extracted images (auto-saved)")
        print(f"  - tables/          : Extracted tables (JSON + MD)")
        print(f"  - summary.json     : Extraction summary")
        print()
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print()


def example_mineru_via_api():
    """Example API request for MinerU extraction."""
    print("=" * 70)
    print("Example 4: API Request for MinerU")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print("Content-Type: application/json")
    print()
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["mineru"]')
    print('}')
    print()
    print("Response includes:")
    print('{')
    print('  "extraction_results": [{')
    print('    "library_name": "mineru",')
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
    print("Plus all outputs saved to: results/{timestamp}/mineru/")
    print()


def example_mineru_comparison():
    """Example comparing MinerU with other extractors."""
    print("=" * 70)
    print("Example 5: MinerU vs Other Extractors")
    print("=" * 70)
    
    print("POST /api/v1/extract")
    print('{')
    print('  "pdf_path": "./sample-pdfs/test.pdf",')
    print('  "libraries": ["pypdf", "pdfplumber", "pymupdf", "docling", "mineru"]')
    print('}')
    print()
    print("MinerU advantages:")
    print("  ✓ Advanced layout analysis")
    print("  ✓ Automatic OCR fallback")
    print("  ✓ High-quality text extraction")
    print("  ✓ Multiple output formats (Markdown, JSON)")
    print("  ✓ Image and table extraction")
    print("  ✓ Rich metadata")
    print()
    print("Trade-offs:")
    print("  - May be slower than PyMuPDF")
    print("  - Higher memory usage")
    print("  - More dependencies")
    print()


def example_mineru_vs_docling():
    """Compare MinerU and Docling extractors."""
    print("=" * 70)
    print("Example 6: MinerU vs Docling")
    print("=" * 70)
    
    print("Both extractors provide similar features:")
    print()
    print("Common Features:")
    print("  ✓ Markdown export")
    print("  ✓ JSON structure export")
    print("  ✓ Image extraction")
    print("  ✓ Table extraction")
    print("  ✓ Layout analysis")
    print()
    print("MinerU Specific:")
    print("  ✓ Automatic OCR fallback")
    print("  ✓ UNIPipe auto-detection")
    print("  ✓ Optimized for complex layouts")
    print()
    print("Docling Specific:")
    print("  ✓ Document understanding focus")
    print("  ✓ Rich document metadata")
    print("  ✓ More detailed structure analysis")
    print()
    print("Recommendation:")
    print("  - Use MinerU for: Complex layouts, scanned PDFs, OCR needs")
    print("  - Use Docling for: Document understanding, metadata extraction")
    print("  - Try both and compare results!")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 16 + "MINERU EXTRACTOR EXAMPLES" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    # Run examples
    example_mineru_basic()
    example_mineru_with_benchmark()
    example_mineru_outputs()
    example_mineru_via_api()
    example_mineru_comparison()
    example_mineru_vs_docling()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nNote: Install MinerU first: pip install magic-pdf[full]")
