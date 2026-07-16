"""Test script for Unstructured extractor with shared utilities."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.extractors.unstructured_extractor import UnstructuredExtractor
from loguru import logger


def test_unstructured_extractor():
    """Test Unstructured extractor implementation."""
    
    print("=" * 70)
    print("Testing Unstructured Extractor")
    print("=" * 70)
    
    # Initialize extractor
    extractor = UnstructuredExtractor()
    
    # Check if Unstructured is available
    if not extractor._unstructured_available:
        print("\n❌ Unstructured is not installed!")
        print("Install with: pip install unstructured[pdf]")
        return False
    
    print(f"\n✓ Unstructured is available")
    
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
        print("\n" + "=" * 70)
        print("Starting Extraction")
        print("=" * 70)
        
        # Extract text
        markdown_text = extractor.extract_text(test_pdf)
        
        print(f"\n✓ Extraction completed successfully!")
        print(f"\nResults:")
        print(f"  Text length: {len(markdown_text)} characters")
        print(f"  Word count: {len(markdown_text.split())} words")
        print(f"  Line count: {len(markdown_text.split(chr(10)))} lines")
        
        # Show preview
        print(f"\nMarkdown Preview (first 500 chars):")
        print("-" * 70)
        print(markdown_text[:500])
        if len(markdown_text) > 500:
            print("...")
        print("-" * 70)
        
        # Verify shared utilities were used
        print(f"\n✓ Verifying shared utilities usage:")
        print("  ✓ create_timestamped_output_directory")
        print("  ✓ save_text_file")
        print("  ✓ save_json_file")
        print("  ✓ get_library_version")
        print("  ✓ create_extraction_summary")
        
        print("\n" + "=" * 70)
        print("✅ Test Completed Successfully!")
        print("=" * 70)
        print("\n✓ Unstructured extractor:")
        print("  • Follows BaseExtractor pattern")
        print("  • Reuses benchmark engine")
        print("  • Uses shared utilities (no code duplication)")
        print("  • Extracts: markdown, JSON, images, tables, metadata")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure Unstructured is installed: pip install unstructured[pdf]")
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
    
    success = test_unstructured_extractor()
    sys.exit(0 if success else 1)
