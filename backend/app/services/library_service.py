"""Library service for managing extraction libraries."""

from typing import List, Optional
import importlib.util

from app.extractors.registry import extractor_registry
from app.extractors.base_extractor import AvailabilityStatus
from app.models.library import Library, LibraryStatus


class LibraryService:
    """Service for managing PDF extraction libraries via the registry."""

    def __init__(self):
        """Initialize library service."""
        self._cache: Optional[List[Library]] = None

    def get_all_libraries(self, force_refresh: bool = False) -> List[Library]:
        """
        Get information about all registered libraries.

        Availability and version are read live from each extractor's
        dependency diagnostics, so a missing dependency is reported as
        ``not_installed`` (or ``error``) without crashing the app.

        Args:
            force_refresh: Force refresh of library status

        Returns:
            List of Library objects with status information
        """
        if self._cache is not None and not force_refresh:
            return self._cache

        libraries: List[Library] = []
        for library_id in extractor_registry.list_ids():
            extractor = extractor_registry.get(library_id)
            if extractor is None:
                continue
            info = extractor.get_info()
            status = self._map_status(info.status)
            libraries.append(
                Library(
                    name=info.library_id,
                    display_name=info.display_name,
                    version=info.version,
                    description=info.description,
                    status=status,
                    capabilities=info.capabilities,
                    performance_notes=info.performance_notes,
                )
            )

        self._cache = libraries
        return libraries

    def _map_status(self, status: AvailabilityStatus) -> LibraryStatus:
        if status == AvailabilityStatus.AVAILABLE:
            return LibraryStatus.AVAILABLE
        if status == AvailabilityStatus.ERROR:
            return LibraryStatus.ERROR
        return LibraryStatus.NOT_INSTALLED

    def get_library_by_name(self, name: str) -> Optional[Library]:
        """
        Get library information by name.

        Args:
            name: Library id

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

    def get_dependency_diagnostics(self, name: str) -> Optional[dict]:
        """Return raw dependency diagnostics for a library id."""
        extractor = extractor_registry.get(name)
        if extractor is None:
            return None
        return extractor.get_info().to_dict()

    def clear_cache(self) -> None:
        """Clear the library cache."""
        self._cache = None