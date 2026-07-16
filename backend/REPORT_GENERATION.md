# Automatic Benchmark Report Generation

The PDF Extraction Benchmark System automatically generates comprehensive markdown reports after each benchmark execution.

## Report Location

Reports are saved to:
```
results/{timestamp}/report.md
```

Example:
```
results/2026_07_15_143022/report.md
```

## Report Sections

### 1. 📊 Overview
- Document information (name, size, pages)
- Libraries tested count
- Success/failure summary
- Fastest library

### 2. 💻 Machine Information
- Operating System
- Architecture
- Processor details
- CPU cores and frequency
- Total memory
- Python version

### 3. 🔬 Benchmark Results
Detailed results for each library:
- Status (success/failed)
- Performance metrics:
  - Execution time (ms)
  - Peak memory (MB)
  - Average CPU (%)
- Output information:
  - Markdown size
  - JSON size
  - Images extracted
  - Tables extracted

### 4. ⚖️ Performance Comparison
- Comparison table with all metrics
- Category winners:
  - Fastest execution
  - Least memory
  - Least CPU
  - Most complete output

### 5. ✅ ❌ Pros and Cons Analysis
For each library:
- **Pros**: Speed, memory efficiency, features
- **Cons**: Limitations and weaknesses
- Library-specific characteristics

### 6. 💡 Recommendations
- Best library for speed
- Best library for memory efficiency
- Best library for feature completeness
- Overall balanced recommendation
- Use case specific recommendations:
  - Short documents (< 10 pages)
  - Medium documents (10-50 pages)
  - Large documents (> 50 pages)
- Special requirements:
  - OCR support
  - Table extraction
  - Image extraction
  - Structure preservation

## Usage

### Option 1: Using ExtractionService

```python
from pathlib import Path
from app.services.extraction_service import ExtractionService

# Initialize service
service = ExtractionService()

# Run benchmark with automatic report generation
results, report_path = service.run_benchmark_with_report(
    pdf_path=Path("data/sample.pdf"),
    library_names=["pypdf", "pdfplumber", "pymupdf", "docling"],
    output_dir=Path("results"),
)

print(f"Report generated: {report_path}")
```

### Option 2: Using ReportService Directly

```python
from pathlib import Path
from app.services.report_service import ReportService

# Prepare benchmark results
benchmark_results = {
    "PyPDF": {
        "status": "success",
        "execution_time_ms": 856.23,
        "peak_memory_mb": 89.4,
        "avg_cpu_percent": 28.5,
        "outputs": {
            "markdown_size": 12340,
            "json_size": 8500,
            "images_count": 0,
            "tables_count": 0,
        }
    },
    "Docling": {
        "status": "success",
        "execution_time_ms": 1234.56,
        "peak_memory_mb": 128.5,
        "avg_cpu_percent": 45.2,
        "outputs": {
            "markdown_size": 15420,
            "json_size": 23450,
            "images_count": 3,
            "tables_count": 2,
        }
    }
}

pdf_info = {
    "name": "sample-document.pdf",
    "size": 2457600,
    "pages": 45
}

# Generate report
service = ReportService()
report_path = service.generate_report(
    benchmark_results=benchmark_results,
    pdf_info=pdf_info,
    output_dir=Path("results/2026_07_15_143022")
)

print(f"Report saved to: {report_path}")
```

## Example Report Structure

```markdown
# PDF Extraction Benchmark Report

**Generated:** 2026-07-15 14:30:22

---

## 📊 Overview

**Document:** annual-report-2025.pdf
**File Size:** 2.34 MB
**Pages:** 45

**Libraries Tested:** 6
**Successful Extractions:** 5 ✅
**Failed Extractions:** 1 ❌

**Fastest Library:** PyMuPDF (654.32 ms)

## 💻 Machine Information

| Property | Value |
|----------|-------|
| Operating System | Windows 11 |
| Processor | Intel Core i7-12700K |
| CPU Cores | 8 physical, 16 logical |
| Total Memory | 32.00 GB |
| Python Version | 3.12.0 |

## 🔬 Benchmark Results

### PyPDF

**Status:** ✅ Success

**Performance Metrics:**
- **Execution Time:** 856.23 ms
- **Peak Memory:** 89.40 MB
- **Average CPU:** 28.50%

...

## ⚖️ Performance Comparison

| Library | Time (ms) | Memory (MB) | CPU (%) | Output Size |
|---------|-----------|-------------|---------|-------------|
| PyMuPDF | 654.32 | 78.60 | 35.20 | 14.21 KB |
| PyPDF | 856.23 | 89.40 | 28.50 | 12.06 KB |
...

### 🏆 Category Winners
- **Fastest Execution:** PyMuPDF (654.32 ms)
- **Least Memory:** PyMuPDF (78.60 MB)
- **Least CPU:** PyPDF (28.50%)
- **Most Complete Output:** MinerU (4 images, 3 tables)

## ✅ ❌ Pros and Cons Analysis

### PyPDF
**Pros:**
- ⚡ Very fast execution (< 1 second)
- 💾 Low memory usage (< 100 MB)
- 🔧 Simple and lightweight

**Cons:**
- 📷 No image extraction
- 📋 No table extraction
- ⚠️ Basic extraction capabilities

...

## 💡 Recommendations

### Best Library for Your Use Case

**For Speed:** Use **PyMuPDF** (654.32 ms)

**For Memory Efficiency:** Use **PyMuPDF** (78.60 MB)

**For Feature Completeness:** Use **MinerU** (4 images, 3 tables)

### Overall Recommendation

**Best Balanced Choice:** **PyMuPDF**

This library offers the best balance of:
- Execution speed
- Memory efficiency
- Feature completeness

...
```

## Report Features

### Automatic Analysis
- Performance comparison across all libraries
- Winner identification for each category
- Balanced scoring algorithm
- Use case specific recommendations

### Intelligent Recommendations
- Speed-optimized choice
- Memory-efficient choice
- Feature-complete choice
- Balanced best overall choice
- Document size considerations
- Special requirement matching

### Rich Formatting
- Emoji indicators for quick scanning
- Tables for easy comparison
- Sections for organized reading
- Clear status indicators
- Human-readable metrics

## API Integration

The report generation is automatically triggered when using the benchmark API:

```python
POST /api/v1/benchmark/run
{
  "pdf_path": "data/sample.pdf",
  "libraries": ["pypdf", "docling", "mineru"],
  "generate_report": true  // Automatic report generation
}
```

Response includes:
```json
{
  "benchmark_id": "bench_2026_07_15_143022",
  "results": [...],
  "report_path": "results/2026_07_15_143022/report.md",
  "report_url": "/api/v1/reports/bench_2026_07_15_143022"
}
```

## Configuration

Report generation can be customized:

```python
from app.services.report_service import ReportService

service = ReportService()

# Generate with custom settings
report_path = service.generate_report(
    benchmark_results=results,
    pdf_info=pdf_info,
    output_dir=Path("custom/path"),
)
```

## Benefits

1. **Automatic**: No manual report creation needed
2. **Comprehensive**: All metrics and recommendations in one place
3. **Shareable**: Markdown format easy to share and version control
4. **Actionable**: Clear recommendations for library selection
5. **Professional**: Well-formatted and organized
6. **Portable**: Plain text, works everywhere

## See Also

- `examples/benchmark_with_report_usage.py` - Example usage
- `app/services/report_service.py` - Report generation implementation
- `app/services/extraction_service.py` - Integration with benchmark engine
