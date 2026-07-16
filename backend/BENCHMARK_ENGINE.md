# Benchmark Engine Documentation

## Overview

The Benchmark Engine provides comprehensive performance monitoring for PDF extraction operations. It measures execution time, memory usage, and CPU utilization using `psutil`.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           BenchmarkEngine                       │
│  (Orchestrates extraction + monitoring)         │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│ PerformanceMonitor  │   │   BaseExtractor     │
│  (psutil tracking)  │   │  (PDF extraction)   │
└─────────────────────┘   └─────────────────────┘
         │                         │
         └────────────┬────────────┘
                      ▼
            ┌─────────────────────┐
            │  ExtractionResult   │
            │  + Performance Data │
            └─────────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  ResultStorageService│
            │  (Save to disk)      │
            └─────────────────────┘
                      │
                      ▼
          results/{timestamp}/
            ├── benchmark.json
            ├── metadata.json
            └── extraction_*.json
```

---

## Components

### 1. PerformanceMonitor

**Location:** `app/benchmark/performance_monitor.py`

**Purpose:** Real-time CPU and memory monitoring during execution

**Features:**
- Runs in separate thread for accurate sampling
- Configurable sampling interval (default: 50ms)
- Tracks both peak and average metrics
- Context manager support

**Usage:**
```python
from app.benchmark.performance_monitor import PerformanceMonitor

# Method 1: Manual start/stop
monitor = PerformanceMonitor(sampling_interval_ms=50)
monitor.start()
# ... do work ...
metrics = monitor.stop()

# Method 2: Context manager
with PerformanceMonitor() as monitor:
    # ... do work ...
    pass
metrics = monitor.stop()

# Access metrics
print(f"Elapsed: {metrics.elapsed_time_ms}ms")
print(f"Peak Memory: {metrics.peak_memory_mb}MB")
print(f"Avg CPU: {metrics.average_cpu_percent}%")
```

**Metrics Collected:**
- `elapsed_time_ms` - Total execution time
- `peak_memory_mb` - Maximum memory used (RSS)
- `average_cpu_percent` - Average CPU utilization
- `memory_samples` - All memory samples
- `cpu_samples` - All CPU samples

---

### 2. BenchmarkEngine

**Location:** `app/benchmark/benchmark_engine.py`

**Purpose:** Wrapper for extraction with automatic performance monitoring

**Features:**
- Wraps any extraction function
- Automatic monitoring start/stop
- Error handling
- Text statistics calculation
- Page estimation

**Usage:**
```python
from app.benchmark.benchmark_engine import BenchmarkEngine

engine = BenchmarkEngine(sampling_interval_ms=50)

# Run benchmarked extraction
result = engine.run_extraction(
    extraction_func=extractor.extract_text,
    pdf_path=Path("document.pdf"),
    library_name="pypdf",
)

# Result includes performance metrics
print(f"Success: {result.success}")
print(f"Time: {result.execution_time_ms}ms")
print(f"Memory: {result.memory_usage_mb}MB")
print(f"CPU: {result.cpu_usage_percent}%")
print(f"Text length: {result.char_count} chars")
```

**Process Flow:**
1. Create PerformanceMonitor
2. Start monitoring
3. Execute extraction function
4. Stop monitoring
5. Calculate text statistics
6. Return ExtractionResult with metrics

---

### 3. ResultStorageService

**Location:** `app/benchmark/result_storage.py`

**Purpose:** Store benchmark results to disk in structured format

**Features:**
- Timestamped directories
- Multiple JSON files per result
- Metadata generation
- Result listing and loading

**Storage Structure:**
```
results/
└── 20260715_103045_123/
    ├── benchmark.json       # Complete benchmark data
    ├── metadata.json        # Summary and metadata
    ├── extraction_pypdf.json
    ├── extraction_pdfplumber.json
    └── extraction_pymupdf.json
```

**Usage:**
```python
from app.benchmark.result_storage import ResultStorageService

storage = ResultStorageService()

# Store benchmark result
result_dir = storage.store_benchmark_result(benchmark_result)
print(f"Results saved to: {result_dir}")

# List all stored results
result_dirs = storage.list_stored_results()

# Load specific result
data = storage.load_benchmark_result(result_dir)
```

**File Contents:**

**benchmark.json:**
```json
{
  "benchmark_id": "uuid",
  "pdf_filename": "document.pdf",
  "created_at": "2026-07-15T10:30:45.123Z",
  "total_duration_ms": 1234.56,
  "summary": {
    "fastest_library": "pymupdf",
    "most_efficient_memory": "pypdf",
    "most_text_extracted": "pdfplumber"
  },
  "extraction_results": [...]
}
```

**metadata.json:**
```json
{
  "benchmark_id": "uuid",
  "pdf_filename": "document.pdf",
  "summary": {
    "total_libraries_tested": 3,
    "successful_extractions": 2,
    "failed_extractions": 1,
    "fastest_library": "pymupdf"
  },
  "performance_comparison": {
    "execution_times": {...},
    "memory_usage": {...},
    "cpu_usage": {...}
  }
}
```

---

## Integration

### Updated BaseExtractor

All extractors now implement two methods:

```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractionResult:
        """Legacy method - returns complete result"""
        pass
    
    @abstractmethod
    def extract_text(self, pdf_path: Path) -> str:
        """New method - returns only text for benchmarking"""
        pass
```

### ExtractionService

Updated to use BenchmarkEngine:

```python
class ExtractionService:
    def __init__(self, benchmark_engine: Optional[BenchmarkEngine] = None):
        self.benchmark_engine = benchmark_engine or BenchmarkEngine()
    
    def extract_with_library(self, pdf_path, library_name):
        # Uses benchmark_engine.run_extraction()
        # Returns ExtractionResult with performance metrics
        pass
```

### BenchmarkService

Updated to use ResultStorageService:

```python
class BenchmarkService:
    def __init__(
        self,
        extraction_service: ExtractionService,
        history_service: HistoryService,
        result_storage: ResultStorageService = None,
    ):
        self.result_storage = result_storage or ResultStorageService()
    
    def run_benchmark(self, pdf_document, library_names):
        # Runs extraction
        # Calculates summary
        # Saves to history
        # Stores results to disk ← NEW
        return benchmark_result
```

---

## API Flow

```
POST /api/v1/extract
    │
    ├─> BenchmarkService.run_benchmark()
    │       │
    │       ├─> ExtractionService.extract_with_multiple_libraries()
    │       │       │
    │       │       ├─> For each library:
    │       │       │   ├─> BenchmarkEngine.run_extraction()
    │       │       │   │       │
    │       │       │   │       ├─> PerformanceMonitor.start()
    │       │       │   │       ├─> extractor.extract_text()
    │       │       │   │       ├─> PerformanceMonitor.stop()
    │       │       │   │       └─> Return ExtractionResult + metrics
    │       │       │   │
    │       │       │   └─> Collect all results
    │       │       │
    │       │       └─> Return List[ExtractionResult]
    │       │
    │       ├─> BenchmarkResult.calculate_summary()
    │       ├─> HistoryService.add_history()
    │       ├─> ResultStorageService.store_benchmark_result() ← NEW
    │       │       │
    │       │       └─> Creates: results/{timestamp}/
    │       │                     ├── benchmark.json
    │       │                     ├── metadata.json
    │       │                     └── extraction_*.json
    │       │
    │       └─> Return BenchmarkResult
    │
    └─> Return API Response
```

---

## Performance Metrics

### Time Measurement
- **Method:** `time.time()` before and after extraction
- **Unit:** Milliseconds (ms)
- **Precision:** Sub-millisecond

### Memory Measurement
- **Method:** `psutil.Process().memory_info().rss`
- **Sampling:** Every 50ms (configurable)
- **Metric:** Peak RSS (Resident Set Size) in MB
- **Accuracy:** Process-specific memory usage

### CPU Measurement
- **Method:** `psutil.Process().cpu_percent()`
- **Sampling:** Every 50ms (configurable)
- **Metric:** Average CPU percentage
- **Accuracy:** Process-specific CPU time

---

## Configuration

### Sampling Interval

Adjust monitoring frequency:

```python
# More frequent sampling (more accurate, more overhead)
engine = BenchmarkEngine(sampling_interval_ms=25)

# Less frequent sampling (less accurate, less overhead)
engine = BenchmarkEngine(sampling_interval_ms=100)

# Default: 50ms (good balance)
engine = BenchmarkEngine()
```

**Recommendations:**
- Fast extractions (< 1s): 25-50ms
- Normal extractions (1-10s): 50-100ms
- Long extractions (> 10s): 100-200ms

---

## Example: Complete Workflow

```python
from pathlib import Path
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.benchmark.result_storage import ResultStorageService
from app.extractors.pypdf_extractor import PyPDFExtractor

# 1. Create components
engine = BenchmarkEngine(sampling_interval_ms=50)
storage = ResultStorageService()
extractor = PyPDFExtractor()

# 2. Run benchmarked extraction
result = engine.run_extraction(
    extraction_func=extractor.extract_text,
    pdf_path=Path("document.pdf"),
    library_name="pypdf",
)

# 3. Check results
if result.success:
    print(f"✓ Extracted {result.char_count} characters")
    print(f"  Time: {result.execution_time_ms:.2f}ms")
    print(f"  Memory: {result.memory_usage_mb:.2f}MB")
    print(f"  CPU: {result.cpu_usage_percent:.1f}%")
else:
    print(f"✗ Failed: {result.error_message}")

# 4. Store results (for BenchmarkResult)
# This is done automatically by BenchmarkService
```

---

## Testing

### Unit Tests

```python
def test_performance_monitor():
    monitor = PerformanceMonitor(sampling_interval_ms=10)
    
    monitor.start()
    time.sleep(0.1)  # Simulate work
    metrics = monitor.stop()
    
    assert metrics.elapsed_time_ms >= 100
    assert len(metrics.memory_samples) > 0
    assert len(metrics.cpu_samples) > 0

def test_benchmark_engine():
    engine = BenchmarkEngine()
    
    def dummy_extraction(pdf_path):
        time.sleep(0.05)
        return "Sample text"
    
    result = engine.run_extraction(
        extraction_func=dummy_extraction,
        pdf_path=Path("test.pdf"),
        library_name="test",
    )
    
    assert result.success
    assert result.execution_time_ms >= 50
    assert result.char_count > 0
```

---

## Troubleshooting

### High Memory Usage

**Issue:** Memory samples show excessive usage

**Solutions:**
- Check for memory leaks in extraction code
- Process PDFs in smaller batches
- Clear cached data between extractions

### Inaccurate CPU Metrics

**Issue:** CPU percentage seems wrong

**Solutions:**
- Increase sampling frequency
- Ensure extraction is CPU-bound (not I/O-bound)
- Check for multi-threading in extraction library

### Missing Samples

**Issue:** Few or no samples collected

**Solutions:**
- Decrease sampling interval
- Ensure extraction takes enough time
- Check monitoring thread isn't blocked

---

## Performance Impact

### Overhead

**Memory:** ~10-20KB per second of monitoring  
**CPU:** ~0.5-1% additional CPU usage  
**Thread:** One additional monitoring thread

### Recommendations

- Use default 50ms interval for most cases
- Disable for quick benchmarks (< 100ms)
- Increase interval for long-running tasks (> 60s)

---

## Future Enhancements

1. **GPU Monitoring** - Track GPU usage for GPU-accelerated extraction
2. **Disk I/O** - Monitor read/write operations
3. **Network I/O** - Track network usage
4. **Real-time Visualization** - Live performance graphs
5. **Comparative Analysis** - Compare across multiple runs
6. **Anomaly Detection** - Flag unusual performance patterns

---

**Created:** 2026-07-15  
**Status:** Implemented and Ready for Use
