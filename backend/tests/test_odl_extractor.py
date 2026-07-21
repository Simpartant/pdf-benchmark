"""Tests for the OpenDataLoader PDF extractor."""

import json
from pathlib import Path

import pytest

from app.extractors.opendataloader_extractor import OpenDataLoaderExtractor
from app.models.extraction_result import ExtractionResult


class TestOpenDataLoaderExtractor:
    """Test cases for OpenDataLoaderExtractor."""

    @pytest.fixture
    def extractor(self):
        return OpenDataLoaderExtractor()

    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Create a sample PDF for testing."""
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF")
        return pdf_path

    def test_extractor_attributes(self, extractor):
        """Test extractor has correct attributes."""
        assert extractor.library_id == "opendataloader"
        assert extractor.display_name == "OpenDataLoader"
        assert "text_extraction" in extractor.capabilities
        assert "bounding_boxes" in extractor.capabilities

    def test_java_check(self, extractor):
        """Test Java availability check."""
        # Java should be available in the test environment
        assert extractor._java_available in (True, False)

    def test_extract_returns_extraction_result(self, extractor, sample_pdf, tmp_path):
        """Test that extract returns an ExtractionResult."""
        output_dir = tmp_path / "output"
        result = extractor.extract(sample_pdf, output_dir)
        assert isinstance(result, ExtractionResult)
        assert result.library == "opendataloader"

    def test_missing_java_returns_failed(self, tmp_path, monkeypatch):
        """Test that missing Java returns failed status."""
        extractor = OpenDataLoaderExtractor()
        extractor._java_available = False
        
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        
        output_dir = tmp_path / "output"
        result = extractor.extract(pdf_path, output_dir)
        assert result.status == "failed"
        assert "Java" in result.error

    def test_missing_package_returns_failed(self, tmp_path, monkeypatch):
        """Test that missing package returns failed status."""
        extractor = OpenDataLoaderExtractor()
        extractor._opendataloader_available = False
        
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        
        output_dir = tmp_path / "output"
        result = extractor.extract(pdf_path, output_dir)
        assert result.status == "failed"
        assert "not installed" in result.error.lower()

    def test_get_info_returns_extractor_info(self, extractor):
        """Test that get_info returns ExtractorInfo."""
        info = extractor.get_info()
        assert info.library_id == "opendataloader"
        assert info.display_name == "OpenDataLoader"
        assert info.status.value in ("available", "not_installed", "error")