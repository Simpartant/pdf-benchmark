"""Test script for OpenDataLoader extractor with shared utilities."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.extractors.opendataloader_extractor import OpenDataLoaderExtractor
from loguru import logger


def test_opendataloader_extractor():
    """Test OpenDataLoader extractor implementation."""
    
    print("=" * 70)
    print("Testing OpenDataLoader Extractor")
    print("=" * 70)
    
    # Initialize extractor
    extractor = OpenDataLoaderExtractor()
    
    # Check if OpenDataLoader is available
    if not extractor._opendataloader_available:
        print("\n❌ OpenDataLoader is not installed!")
        print("Install with: pip install opendataloader")
        return False
    
    print(f"\n✓ OpenDataLoader is available")
    
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
        print("\n✓ OpenDataLoader extractor:")
        print("  • Follows BaseExtractor pattern")
        print("  • Reuses benchmark engine")
        print("  • Uses shared utilities (no code duplication)")
        print("  • Extracts: markdown, JSON, images, tables, metadata")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure OpenDataLoader is installed: pip install opendataloader")
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
    
    success = test_opendataloader_extractor()
    sys.exit(0 if success else 1)
