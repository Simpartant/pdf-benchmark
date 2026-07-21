"""Tests for the extractor registry and normalized BaseExtractor interface."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.extractors.registry import extractor_registry, ExtractorRegistry
from app.extractors.base_extractor import (
    BaseExtractor,
    AvailabilityStatus,
    ExtractorInfo,
)
from app.models.extraction_result import ExtractionResult


class FakeExtractor(BaseExtractor):
    """Minimal extractor used to verify the registry contract."""

    library_id = "fake"
    display_name = "Fake"
    required_modules = ["nonexistent_module_xyz"]

    def extract(self, pdf_path, output_dir, options=None):
        return ExtractionResult(
            library=self.library_id,
            original_filename=pdf_path.name,
            status="success",
            markdown="# hello",
            page_count=1,
        )


def test_registry_get_known_libraries():
    for lib_id in ("docling", "unstructured", "mineru"):
        extractor = extractor_registry.get(lib_id)
        assert extractor is not None, f"{lib_id} should be registered"
        assert extractor.library_id == lib_id


def test_registry_get_unknown_returns_none():
    assert extractor_registry.get("does_not_exist") is None


def test_registry_list_ids_contains_targets():
    ids = extractor_registry.list_ids()
    for lib_id in ("docling", "unstructured", "mineru"):
        assert lib_id in ids


def test_registry_is_registered():
    assert extractor_registry.is_registered("docling")
    assert not extractor_registry.is_registered("nope")


def test_registry_register_and_get():
    reg = ExtractorRegistry()
    reg.register("fake", FakeExtractor)
    assert reg.is_registered("fake")
    instance = reg.get("fake")
    assert isinstance(instance, FakeExtractor)
    # Cached instance
    assert reg.get("fake") is instance


def test_base_extractor_interface_contract():
    extractor = FakeExtractor()
    # Required attributes
    assert extractor.library_id == "fake"
    assert extractor.display_name == "Fake"
    # Availability: required module is missing -> not_installed, no crash
    assert extractor.is_available() is False
    info = extractor.get_info()
    assert isinstance(info, ExtractorInfo)
    assert info.status == AvailabilityStatus.NOT_INSTALLED
    assert info.version == "unknown"
    assert any("nonexistent_module_xyz" in d.module for d in info.dependencies)
    # Diagnostics present, app did not crash
    assert len(info.diagnostics) >= 1


def test_extractor_info_to_dict_shape():
    extractor = FakeExtractor()
    data = extractor.get_info().to_dict()
    assert data["libraryId"] == "fake"
    assert data["status"] == "not_installed"
    assert "dependencies" in data
    assert "diagnostics" in data


def test_extract_returns_normalized_result(tmp_path):
    extractor = FakeExtractor()
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    out = tmp_path / "out"
    out.mkdir()  # FakeExtractor is a minimal test double; real extractors create this.
    result = extractor.extract(pdf, out)
    assert isinstance(result, ExtractionResult)
    assert result.library == "fake"
    assert result.status == "success"
    assert result.markdown == "# hello"
    assert result.page_count == 1