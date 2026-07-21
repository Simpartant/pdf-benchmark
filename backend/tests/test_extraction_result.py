"""Tests for the normalized ExtractionResult model."""

from datetime import datetime
from uuid import uuid4

from app.models.extraction_result import ExtractionResult


def test_extraction_result_defaults():
    r = ExtractionResult(library="docling", original_filename="a.pdf")
    assert r.library == "docling"
    assert r.status == "success"
    assert r.run_id is not None
    assert r.benchmark_group_id is not None
    assert r.run_id != r.benchmark_group_id


def test_extraction_result_backward_compat_properties():
    r = ExtractionResult(
        library="docling",
        status="success",
        markdown="hello world",
        page_count=3,
        table_count=2,
        image_count=1,
        processing_time_seconds=1.5,
        peak_memory_mb=120.0,
        average_cpu_percent=40.0,
    )
    assert r.library_name == "docling"
    assert r.success is True
    assert r.text_content == "hello world"
    assert r.pages_extracted == 3
    assert r.tables_count == 2
    assert r.images_count == 1
    assert r.execution_time_ms == 1500.0
    assert r.memory_usage_mb == 120.0
    assert r.cpu_usage_percent == 40.0
    assert r.char_count == len("hello world")
    assert r.id == r.run_id


def test_to_dict_normalized_schema():
    r = ExtractionResult(
        library="docling",
        library_version="1.0.0",
        original_filename="a.pdf",
        status="success",
        markdown="# md",
        structured_json={"k": "v"},
        page_count=5,
        table_count=1,
        image_count=2,
        output_files={"markdown": "/x/markdown.md"},
        processing_time_seconds=2.0,
        peak_memory_mb=64.0,
        average_cpu_percent=25.0,
        input_size_bytes=1000,
        output_size_bytes=2000,
        markdown_length=4,
        json_size_bytes=10,
    )
    d = r.to_dict()
    assert d["library"] == "docling"
    assert d["libraryVersion"] == "1.0.0"
    assert d["originalFilename"] == "a.pdf"
    assert d["status"] == "success"
    assert d["markdown"] == "# md"
    assert d["structuredJson"] == {"k": "v"}
    assert d["pageCount"] == 5
    assert d["tableCount"] == 1
    assert d["imageCount"] == 2
    assert d["outputFiles"] == {"markdown": "/x/markdown.md"}
    assert d["processingTimeSeconds"] == 2.0
    assert d["peakMemoryMb"] == 64.0
    assert d["averageCpuPercent"] == 25.0
    assert d["inputSizeBytes"] == 1000
    assert d["outputSizeBytes"] == 2000
    assert d["markdownLength"] == 4
    assert d["jsonSizeBytes"] == 10
    # run identifiers present
    assert "runId" in d and "benchmarkGroupId" in d


def test_from_dict_round_trip():
    original = ExtractionResult(
        library="unstructured",
        library_version="0.9.0",
        original_filename="b.pdf",
        status="failed",
        error="boom",
        page_count=0,
        processing_time_seconds=0.1,
    )
    restored = ExtractionResult.from_dict(original.to_dict())
    assert restored.library == "unstructured"
    assert restored.library_version == "0.9.0"
    assert restored.status == "failed"
    assert restored.error == "boom"
    assert restored.processing_time_seconds == 0.1
    assert restored.run_id == original.run_id
    assert restored.benchmark_group_id == original.benchmark_group_id


def test_from_dict_accepts_legacy_keys():
    legacy = {
        "library_name": "docling",
        "success": True,
        "text_content": "legacy",
        "execution_time_ms": 500.0,
        "memory_usage_mb": 80.0,
        "cpu_usage_percent": 30.0,
        "pages_extracted": 4,
        "output_size_bytes": 999,
    }
    r = ExtractionResult.from_dict(legacy)
    assert r.library == "docling"
    assert r.status == "success"
    assert r.markdown == "legacy"
    assert r.page_count == 4
    assert r.processing_time_seconds == 0.5
    assert r.peak_memory_mb == 80.0
    assert r.output_size_bytes == 999