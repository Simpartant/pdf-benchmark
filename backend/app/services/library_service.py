"""Library service for managing extraction libraries."""

from typing import List, Dict, Optional
import importlib.util

from app.models.library import Library, LibraryStatus


class LibraryService:
    """Service for managing PDF extraction libraries."""

    # Available libraries configuration
    AVAILABLE_LIBRARIES = {
        "pypdf": {
            "display_name": "PyPDF",
            "module": "pypdf",
            "description": "Pure Python PDF library with good stability",
            "capabilities": ["text_extraction", "metadata"],
            "performance_notes": "Good for simple PDFs, slower on complex layouts",
        },
        "pdfplumber": {
            "display_name": "PDFPlumber",
            "module": "pdfplumber",
            "description": "Powerful library for extracting text and tables",
            "capabilities": ["text_extraction", "table_extraction", "layout_analysis"],
            "performance_notes": "Excellent for tables, moderate speed",
        },
        "pymupdf": {
            "display_name": "PyMuPDF",
            "module": "fitz",
            "description": "Fast C-based library with extensive features",
            "capabilities": ["text_extraction", "image_extraction", "rendering", "metadata"],
            "performance_notes": "Fastest option, great for large PDFs",
        },
        "docling": {
            "display_name": "Docling",
            "module": "docling",
            "description": "Advanced document understanding and conversion library",
            "capabilities": [
                "text_extraction",
                "markdown_export",
                "json_export",
                "image_extraction",
                "table_extraction",
                "layout_analysis",
                "metadata_extraction",
            ],
            "performance_notes": "Comprehensive extraction with multiple output formats",
        },
        "mineru": {
            "display_name": "MinerU",
            "module": "magic_pdf",
            "description": "High-quality PDF extraction with layout analysis and OCR support",
            "capabilities": [
                "text_extraction",
                "markdown_export",
                "json_export",
                "image_extraction",
                "table_extraction",
                "layout_analysis",
                "ocr_support",
                "metadata_extraction",
            ],
            "performance_notes": "Advanced layout analysis with automatic OCR fallback",
        },
        "unstructured": {
            "display_name": "Unstructured",
            "module": "unstructured",
            "description": "Universal document processing library with element-based extraction",
            "capabilities": [
                "text_extraction",
                "markdown_export",
                "json_export",
                "image_extraction",
                "table_extraction",
                "element_classification",
                "layout_analysis",
                "metadata_extraction",
            ],
            "performance_notes": "Element-based extraction with high-resolution strategy",
        },
    }

    def __init__(self):
        """Initialize library service."""
        self._cache: Optional[List[Library]] = None

    def get_all_libraries(self, force_refresh: bool = False) -> List[Library]:
        """
        Get information about all available libraries.
        
        Args:
            force_refresh: Force refresh of library status
            
        Returns:
            List of Library objects with status information
        """
        if self._cache is not None and not force_refresh:
            return self._cache

        libraries = []
        for name, config in self.AVAILABLE_LIBRARIES.items():
            library = Library(
                name=name,
                display_name=config["display_name"],
                description=config["description"],
                capabilities=config["capabilities"],
                performance_notes=config["performance_notes"],
            )
            
            # Check if library is installed
            status, version = self._check_library_status(config["module"])
            library.status = status
            library.version = version
            
            libraries.append(library)

        self._cache = libraries
        return libraries

    def get_library_by_name(self, name: str) -> Optional[Library]:
        """
        Get library information by name.
        
        Args:
            name: Library name
            
        Returns:
            Library object or None if not found
        """
        libraries = self.get_all_libraries()
        return next((lib for lib in libraries if lib.name == name), None)

    def get_available_libraries(self) -> List[Library]:
        """
        Get only installed and available libraries.
        
        Returns:
            List of available Library objects
        """
        all_libraries = self.get_all_libraries()
        return [lib for lib in all_libraries if lib.status == LibraryStatus.AVAILABLE]

    def _check_library_status(self, module_name: str) -> tuple[LibraryStatus, Optional[str]]:
        """
        Check if a library module is installed.
        
        Args:
            module_name: Python module name to check
            
        Returns:
            Tuple of (status, version)
        """
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return (LibraryStatus.NOT_INSTALLED, None)
            
            # Try to get version
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, "__version__", "unknown")
                return (LibraryStatus.AVAILABLE, version)
            except Exception:
                return (LibraryStatus.AVAILABLE, "unknown")
                
        except Exception:
            return (LibraryStatus.ERROR, None)

    def clear_cache(self) -> None:
        """Clear the library cache."""
        self._cache = None
