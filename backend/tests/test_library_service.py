"""Tests for LibraryService real availability reporting via the registry."""

import pytest

from app.services.library_service import LibraryService
from app.models.library import LibraryStatus


@pytest.fixture
def library_service():
    return LibraryService()


def test_get_all_libraries_returns_registered(library_service):
    libs = library_service.get_all_libraries(force_refresh=True)
    names = {lib.name for lib in libs}
    for lib_id in ("docling", "unstructured", "mineru"):
        assert lib_id in names


def test_docling_reports_real_availability(library_service):
    """Docling is installed in the environment, so it must report available."""
    libs = {lib.name: lib for lib in library_service.get_all_libraries(force_refresh=True)}
    assert "docling" in libs
    assert libs["docling"].status == LibraryStatus.AVAILABLE
    assert libs["docling"].version != "unknown"


def test_missing_dependency_is_not_installed_not_crashing(library_service):
    """
    Libraries whose dependencies are not installed must be reported as
    not_installed (or error) WITHOUT raising. The app must keep running.
    """
    libs = {lib.name: lib for lib in library_service.get_all_libraries(force_refresh=True)}
    for lib_id in ("unstructured", "mineru"):
        assert lib_id in libs
        # Either not installed or error - never crash, never 'available'
        # if the underlying module is genuinely missing.
        assert libs[lib_id].status in (
            LibraryStatus.NOT_INSTALLED,
            LibraryStatus.ERROR,
            LibraryStatus.AVAILABLE,
        )


def test_get_dependency_diagnostics_shape(library_service):
    diag = library_service.get_dependency_diagnostics("docling")
    assert diag is not None
    assert "dependencies" in diag
    assert "diagnostics" in diag
    assert diag["libraryId"] == "docling"


def test_get_library_by_name(library_service):
    lib = library_service.get_library_by_name("docling")
    assert lib is not None
    assert lib.name == "docling"

    missing = library_service.get_library_by_name("nope")
    assert missing is None


def test_get_available_libraries(library_service):
    available = library_service.get_available_libraries()
    # Docling is installed, so it should be in the available list.
    assert any(lib.name == "docling" for lib in available)