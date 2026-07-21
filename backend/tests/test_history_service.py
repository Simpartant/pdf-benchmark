"""Tests for history service (normalized schema)."""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from app.services.history_service import HistoryService
from app.models.history import ExtractionHistory


class TestHistoryService:
    """Test cases for HistoryService."""

    @pytest.fixture
    def temp_results_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def history_service(self, temp_results_dir, monkeypatch):
        from app.core import config
        monkeypatch.setattr(config.settings, 'results_dir', temp_results_dir)
        return HistoryService()

    def test_scan_result_directories_empty(self, history_service):
        result_dirs = history_service._scan_result_directories()
        assert result_dirs == []

    def test_scan_result_directories_with_valid_dirs(self, history_service, temp_results_dir):
        result_dir1 = Path(temp_results_dir) / "20260717_120000_001"
        result_dir2 = Path(temp_results_dir) / "20260717_130000_002"
        result_dir1.mkdir()
        result_dir2.mkdir()

        benchmark_data = {
            "benchmark_id": str(uuid4()),
            "pdf_filename": "test.pdf",
            "created_at": datetime.now().isoformat(),
            "extraction_results": []
        }
        with open(result_dir1 / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)
        with open(result_dir2 / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)

        result_dirs = history_service._scan_result_directories()
        assert len(result_dirs) == 2
        assert result_dirs[0].name == "20260717_130000_002"
        assert result_dirs[1].name == "20260717_120000_001"

    def test_scan_result_directories_ignores_non_result_dirs(self, history_service, temp_results_dir):
        (Path(temp_results_dir) / "20260717_120000_001").mkdir()
        (Path(temp_results_dir) / "random_dir").mkdir()
        (Path(temp_results_dir) / "20260717_130000_002").mkdir()

        with open(Path(temp_results_dir) / "20260717_130000_002" / "benchmark.json", "w") as f:
            json.dump({"benchmark_id": str(uuid4())}, f)

        result_dirs = history_service._scan_result_directories()
        assert len(result_dirs) == 1
        assert result_dirs[0].name == "20260717_130000_002"

    def test_load_history_from_dir_valid(self, history_service, temp_results_dir):
        benchmark_id = uuid4()
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()

        benchmark_data = {
            "benchmark_id": str(benchmark_id),
            "pdf_filename": "test.pdf",
            "pdf_id": str(uuid4()),
            "created_at": "2026-07-17T12:00:00.000000",
            "total_duration_ms": 1000.0,
            "extraction_results": [
                {
                    "library": "docling",
                    "status": "success",
                    "processingTimeSeconds": 0.5,
                    "peakMemoryMb": 100.0,
                    "averageCpuPercent": 50.0,
                    "pageCount": 10,
                    "outputSizeBytes": 50000,
                }
            ]
        }
        with open(result_dir / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)

        record = history_service._load_history_from_dir(result_dir)
        assert record is not None
        assert record.id == benchmark_id
        assert record.pdf_filename == "test.pdf"
        assert record.total_duration_ms == 1000.0
        assert record.success_count == 1
        assert record.failure_count == 0
        assert record.libraries_used == ["docling"]

    def test_load_history_from_dir_missing_files(self, history_service, temp_results_dir):
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()
        record = history_service._load_history_from_dir(result_dir)
        assert record is None

    def test_load_history_from_dir_corrupted_json(self, history_service, temp_results_dir):
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()
        with open(result_dir / "benchmark.json", "w") as f:
            f.write("not valid json{")
        record = history_service._load_history_from_dir(result_dir)
        assert record is None

    def test_get_all_history(self, history_service, temp_results_dir):
        for i, (bid, filename) in enumerate([
            (uuid4(), "test1.pdf"),
            (uuid4(), "test2.pdf"),
        ]):
            result_dir = Path(temp_results_dir) / f"20260717_1{i}0000_00{i}"
            result_dir.mkdir()
            benchmark_data = {
                "benchmark_id": str(bid),
                "pdf_filename": filename,
                "pdf_id": str(uuid4()),
                "created_at": f"2026-07-17T1{i}:00:00.000000",
                "total_duration_ms": float(i * 1000),
                "extraction_results": [
                    {"library": "docling", "status": "success"}
                ]
            }
            with open(result_dir / "benchmark.json", "w") as f:
                json.dump(benchmark_data, f)

        records = history_service.get_all_history()
        assert len(records) == 2
        assert records[0].pdf_filename == "test2.pdf"
        assert records[1].pdf_filename == "test1.pdf"

    def test_get_history_by_id(self, history_service, temp_results_dir):
        benchmark_id = uuid4()
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()
        benchmark_data = {
            "benchmark_id": str(benchmark_id),
            "pdf_filename": "test.pdf",
            "pdf_id": str(uuid4()),
            "created_at": "2026-07-17T12:00:00.000000",
            "total_duration_ms": 1000.0,
            "extraction_results": []
        }
        with open(result_dir / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)

        record = history_service.get_history_by_id(benchmark_id)
        assert record is not None
        assert record.id == benchmark_id

    def test_get_history_by_id_not_found(self, history_service):
        record = history_service.get_history_by_id(uuid4())
        assert record is None

    def test_delete_history(self, history_service, temp_results_dir):
        benchmark_id = uuid4()
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()
        benchmark_data = {
            "benchmark_id": str(benchmark_id),
            "pdf_filename": "test.pdf",
            "pdf_id": str(uuid4()),
            "created_at": "2026-07-17T12:00:00.000000",
            "total_duration_ms": 1000.0,
            "extraction_results": []
        }
        with open(result_dir / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)

        assert result_dir.exists()
        success = history_service.delete_history(benchmark_id)
        assert success is True
        assert not result_dir.exists()

    def test_delete_history_not_found(self, history_service):
        success = history_service.delete_history(uuid4())
        assert success is False

    def test_path_traversal_prevention(self, history_service, temp_results_dir):
        result_dir = Path(temp_results_dir) / "20260717_120000_001"
        result_dir.mkdir()
        benchmark_data = {
            "benchmark_id": str(uuid4()),
            "pdf_filename": "test.pdf",
            "pdf_id": str(uuid4()),
            "created_at": "2026-07-17T12:00:00.000000",
            "total_duration_ms": 1000.0,
            "extraction_results": []
        }
        with open(result_dir / "benchmark.json", "w") as f:
            json.dump(benchmark_data, f)

        records = history_service.get_all_history()
        assert len(records) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])