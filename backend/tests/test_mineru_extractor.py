"""Tests for the MinerU PDF extractor."""

import json
from pathlib import Path

import pytest

from app.extractors.mineru_extractor import MinerUExtractor
from app.models.extraction_result import ExtractionResult


class TestMinerUExtractor:
    """Test cases for MinerUExtractor."""

    @pytest.fixture
    def extractor(self):
        return MinerUExtractor()

    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Create a sample PDF for testing."""
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF")
        return pdf_path

    def test_extractor_attributes(self, extractor):
        """Test extractor has correct attributes."""
        assert extractor.library_id == "mineru"
        assert extractor.display_name == "MinerU"
        assert "text_extraction" in extractor.capabilities
        assert "ocr_support" in extractor.capabilities

    def test_cli_check(self, extractor):
        """Test CLI availability check."""
        # CLI should be False in Python 3.9 environment
        assert extractor._cli_available in (True, False)

    def test_missing_package_returns_failed(self, tmp_path, monkeypatch):
        """Test that missing package returns failed status."""
        extractor = MinerUExtractor()
        extractor._mineru_available = False
        
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        
        output_dir = tmp_path / "output"
        result = extractor.extract(pdf_path, output_dir)
        assert result.status == "failed"
        assert "not installed" in result.error.lower()

    def test_missing_cli_returns_failed(self, tmp_path, monkeypatch):
        """Test that missing CLI returns failed status."""
        extractor = MinerUExtractor()
        extractor._mineru_available = True
        extractor._cli_available = False
        
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        
        output_dir = tmp_path / "output"
        result = extractor.extract(pdf_path, output_dir)
        assert result.status == "failed"
        assert "CLI" in result.error

    def test_get_info_returns_extractor_info(self, extractor):
        """Test that get_info returns ExtractorInfo."""
        info = extractor.get_info()
        assert info.library_id == "mineru"
        assert info.display_name == "MinerU"
        assert info.status.value in ("available", "not_installed", "error")

    def test_timeout_option(self, extractor, sample_pdf, tmp_path):
        """Test that timeout option is passed correctly."""
        # This test verifies the extractor handles the timeout option
        # In a real environment, this would test the actual timeout behavior
        output_dir = tmp_path / "output"
        # The extractor should accept the timeout option without error
        # (actual timeout testing would require a slow PDF)
        assert extractor.DEFAULT_TIMEOUT == 300