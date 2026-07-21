"""Extractor registry.

Central place that maps a library id to its extractor instance. This
replaces the previous hardcoded dictionaries spread across services
with a single, importable registry.
"""

from typing import Dict, List, Optional

from app.extractors.base_extractor import BaseExtractor
from app.extractors.docling_extractor import DoclingExtractor
from app.extractors.unstructured_extractor import UnstructuredExtractor
from app.extractors.mineru_extractor import MinerUExtractor
from app.extractors.pypdf_extractor import PyPDFExtractor
from app.extractors.pdfplumber_extractor import PDFPlumberExtractor
from app.extractors.pymupdf_extractor import PyMuPDFExtractor


class ExtractorRegistry:
    """
    Registry of all known PDF extractors, keyed by ``library_id``.

    Extractors are instantiated lazily on first access so that a missing
    dependency in one extractor does not prevent the others from loading.
    """

    def __init__(self) -> None:
        # Factory functions avoid importing heavy libraries at import time.
        self._factories: Dict[str, callable] = {
            "docling": DoclingExtractor,
            "unstructured": UnstructuredExtractor,
            "mineru": MinerUExtractor,
            "pypdf": PyPDFExtractor,
            "pdfplumber": PDFPlumberExtractor,
            "pymupdf": PyMuPDFExtractor,
        }
        self._instances: Dict[str, BaseExtractor] = {}

    def register(self, library_id: str, factory: callable) -> None:
        """Register a new extractor factory by library id."""
        self._factories[library_id] = factory
        self._instances.pop(library_id, None)

    def get(self, library_id: str) -> Optional[BaseExtractor]:
        """
        Return the extractor instance for ``library_id``.

        Returns ``None`` if the id is unknown (never raises), so callers
        can gracefully skip unavailable libraries.
        """
        if library_id not in self._factories:
            return None
        if library_id not in self._instances:
            self._instances[library_id] = self._factories[library_id]()
        return self._instances[library_id]

    def get_all(self) -> List[BaseExtractor]:
        """Return instances for every registered library id."""
        return [self.get(lid) for lid in self._factories if self.get(lid) is not None]

    def list_ids(self) -> List[str]:
        """Return all registered library ids."""
        return list(self._factories.keys())

    def is_registered(self, library_id: str) -> bool:
        """Return True if ``library_id`` is registered."""
        return library_id in self._factories


#: Application-wide singleton registry.
extractor_registry = ExtractorRegistry()