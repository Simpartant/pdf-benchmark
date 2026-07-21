"""Tests for the Unstructured PDF extractor."""

import json
from pathlib import Path

import pytest

from app.extractors.unstructured_extractor import UnstructuredExtractor
from app.models.extraction_result import ExtractionResult


class TestUnstructuredExtractor:
    """Test cases for UnstructuredExtractor."""

    @pytest.fixture
    def extractor(self):
        return UnstructuredExtractor()

    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Create a sample PDF for testing."""
        pdf_path = tmp_path / "test.pdf"
        # Create a minimal valid PDF
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF")
        return pdf_path

    def test_extractor_attributes(self, extractor):
        """Test extractor has correct attributes."""
        assert extractor.library_id == "unstructured"
        assert extractor.display_name == "Unstructured"
        assert "text_extraction" in extractor.capabilities
        assert "table_extraction" in extractor.capabilities
        assert "image_extraction" in extractor.capabilities

    def test_strategies_defined(self, extractor):
        """Test supported strategies."""
        assert "auto" in extractor.STRATEGIES
        assert "fast" in extractor.STRATEGIES
        assert "hi_res" in extractor.STRATEGIES
        assert "ocr_only" in extractor.STRATEGIES
        assert extractor.DEFAULT_STRATEGY == "auto"

    def test_extract_returns_extraction_result(self, extractor, sample_pdf, tmp_path):
        """Test that extract returns an ExtractionResult."""
        output_dir = tmp_path / "output"
        result = extractor.extract(sample_pdf, output_dir, {"strategy": "fast"})
        assert isinstance(result, ExtractionResult)
        assert result.library == "unstructured"

    def test_extract_creates_output_files(self, extractor, sample_pdf, tmp_path):
        """Test that extract creates output files."""
        output_dir = tmp_path / "output"
        result = extractor.extract(sample_pdf, output_dir, {"strategy": "fast"})
        assert output_dir.exists()
        assert (output_dir / "markdown.md").exists()
        assert (output_dir / "elements.json").exists()
        assert (output_dir / "metadata.json").exists()

    def test_extract_saves_metadata_with_strategy(self, extractor, sample_pdf, tmp_path):
        """Test that strategy is saved in metadata."""
        output_dir = tmp_path / "output"
        result = extractor.extract(sample_pdf, output_dir, {"strategy": "fast"})
        with open(output_dir / "metadata.json") as f:
            metadata = json.load(f)
        assert metadata["strategy"] == "fast"
        assert metadata["extractor"] == "unstructured"

    def test_invalid_strategy_defaults_to_auto(self, extractor, sample_pdf, tmp_path):
        """Test that invalid strategy defaults to auto."""
        output_dir = tmp_path / "output"
        result = extractor.extract(sample_pdf, output_dir, {"strategy": "invalid"})
        with open(output_dir / "metadata.json") as f:
            metadata = json.load(f)
        assert metadata["strategy"] == "auto"

    def test_missing_pdf_raises_error(self, extractor, tmp_path):
        """Test that missing PDF raises FileNotFoundError."""
        output_dir = tmp_path / "output"
        with pytest.raises(FileNotFoundError):
            extractor.extract(tmp_path / "nonexistent.pdf", output_dir)

    def test_get_info_returns_extractor_info(self, extractor):
        """Test that get_info returns ExtractorInfo."""
        info = extractor.get_info()
        assert info.library_id == "unstructured"
        assert info.display_name == "Unstructured"
        assert info.status.value in ("available", "not_installed", "error")

    def test_unavailable_extractor_returns_failed(self, tmp_path, monkeypatch):
        """Test that unavailable extractor returns failed status."""
        # Create extractor with unavailable state
        extractor = UnstructuredExtractor()
        # Force unavailable
        extractor._unstructured_available = False
        
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")
        
        output_dir = tmp_path / "output"
        result = extractor.extract(pdf_path, output_dir)
        assert result.status == "failed"
        assert "not installed" in result.error.lower()