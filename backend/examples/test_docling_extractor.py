"""Test script for Docling extractor."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.extractors.docling_extractor import DoclingExtractor
from loguru import logger


def test_docling_extractor():
    """Test Docling extractor with a sample PDF."""
    
    print("=" * 60)
    print("Testing Docling Extractor")
    print("=" * 60)
    
    # Initialize extractor
    extractor = DoclingExtractor()
    
    # Check if Docling is available
    if not extractor._docling_available:
        print("\n❌ Docling is not installed!")
        print("Install with: pip install docling")
        return False
    
    print(f"\n✓ Docling is available")
    print(f"  Version: {extractor._get_docling_version()}")
    
    # Check for test PDF
    test_pdf = Path("test_files/sample.pdf")
    
    if not test_pdf.exists():
        print(f"\n⚠ Test PDF not found: {test_pdf}")
        print("  Create a 'test_files' directory and add 'sample.pdf'")
        print("  Or provide a PDF path when calling this script:")
        print(f"  python {Path(__file__).name} path/to/your.pdf")
        return False
    
    print(f"\n✓ Test PDF found: {test_pdf}")
    
    # Test extraction
    try:
        print("\n" + "=" * 60)
        print("Starting Extraction")
        print("=" * 60)
        
        # Extract text
        markdown_text = extractor.extract_text(test_pdf)
        
        print(f"\n✓ Extraction completed successfully!")
        print(f"\nResults:")
        print(f"  Text length: {len(markdown_text)} characters")
        print(f"  Word count: {len(markdown_text.split())} words")
        print(f"  Line count: {len(markdown_text.split(chr(10)))} lines")
        
        # Show preview
        print(f"\nMarkdown Preview (first 500 chars):")
        print("-" * 60)
        print(markdown_text[:500])
        if len(markdown_text) > 500:
            print("...")
        print("-" * 60)
        
        print("\n" + "=" * 60)
        print("Test Completed Successfully!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure Docling is installed: pip install docling")
        return False
        
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        logger.exception("Extraction error")
        return False


if __name__ == "__main__":
    # Check for PDF path argument
    if len(sys.argv) > 1:
        test_pdf = Path(sys.argv[1])
        if test_pdf.exists():
            print(f"Using provided PDF: {test_pdf}")
            # Override test_pdf location
            import shutil
            test_dir = Path("test_files")
            test_dir.mkdir(exist_ok=True)
            shutil.copy(test_pdf, test_dir / "sample.pdf")
    
    success = test_docling_extractor()
    sys.exit(0 if success else 1)
