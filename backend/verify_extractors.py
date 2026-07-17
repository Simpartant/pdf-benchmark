"""Quick test to verify all extractors are working."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all extractors can be imported."""
    print("=" * 70)
    print("Testing Extractor Imports")
    print("=" * 70)
    
    extractors = [
        ("PyPDF", "app.extractors.pypdf_extractor", "PyPDFExtractor"),
        ("PDFPlumber", "app.extractors.pdfplumber_extractor", "PDFPlumberExtractor"),
        ("PyMuPDF", "app.extractors.pymupdf_extractor", "PyMuPDFExtractor"),
        ("Docling", "app.extractors.docling_extractor", "DoclingExtractor"),
        ("MinerU", "app.extractors.mineru_extractor", "MinerUExtractor"),
        ("Unstructured", "app.extractors.unstructured_extractor", "UnstructuredExtractor"),
    ]
    
    results = []
    for name, module_path, class_name in extractors:
        try:
            module = __import__(module_path, fromlist=[class_name])
            extractor_class = getattr(module, class_name)
            extractor = extractor_class()
            results.append((name, "✓", f"Ready (library: {extractor.library_name})"))
        except Exception as e:
            results.append((name, "✗", f"Error: {str(e)[:50]}"))
    
    # Print results
    print()
    for name, status, message in results:
        print(f"{status} {name:15} - {message}")
    
    # Summary
    success_count = sum(1 for _, status, _ in results if status == "✓")
    print()
    print("=" * 70)
    print(f"Summary: {success_count}/{len(results)} extractors ready")
    print("=" * 70)
    
    return success_count == len(results)


def test_library_availability():
    """Test if underlying libraries are available."""
    print("\n" + "=" * 70)
    print("Testing Library Availability")
    print("=" * 70)
    
    libraries = [
        ("pypdf", "pypdf"),
        ("pdfplumber", "pdfplumber"),
        ("pymupdf", "pymupdf"),
        ("docling", "docling"),
        ("magic-pdf", "magic_pdf"),
        ("unstructured", "unstructured"),
        ("pillow-heif", "pillow_heif"),
    ]
    
    results = []
    for name, module_name in libraries:
        try:
            __import__(module_name)
            try:
                from importlib.metadata import version
                ver = version(name)
                results.append((name, "✓", f"v{ver}"))
            except:
                results.append((name, "✓", "version unknown"))
        except ImportError:
            results.append((name, "✗", "Not installed"))
    
    # Print results
    print()
    for name, status, message in results:
        print(f"{status} {name:15} - {message}")
    
    success_count = sum(1 for _, status, _ in results if status == "✓")
    print()
    print("=" * 70)
    print(f"Summary: {success_count}/{len(results)} libraries installed")
    print("=" * 70)
    
    return success_count >= len(results) - 1  # Allow 1 missing (optional library)


if __name__ == "__main__":
    print("\n🔍 PDF Benchmark - Extractor Verification\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test library availability
    libraries_ok = test_library_availability()
    
    # Final result
    print("\n" + "=" * 70)
    if imports_ok and libraries_ok:
        print("✅ ALL SYSTEMS READY!")
        print("\nYou can now:")
        print("  1. Start the backend: uvicorn app.main:app --reload")
        print("  2. Visit API docs: http://localhost:8000/docs")
        print("  3. Run benchmarks on your PDFs")
    else:
        print("⚠️  SOME ISSUES DETECTED")
        print("\nPlease check the errors above and:")
        print("  1. Install missing libraries")
        print("  2. Fix import errors")
        print("  3. Re-run this test")
    print("=" * 70)
    print()
