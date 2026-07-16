# Docling Extractor Implementation

## Overview

The **Docling Extractor** is a comprehensive PDF extraction adapter that extends the base extractor architecture with advanced document understanding capabilities. It extracts PDF content to multiple formats including markdown, JSON, images, tables, and metadata.

---

## Features

### ✅ Multiple Output Formats
- **Markdown**: Clean, formatted text export
- **JSON**: Complete document structure
- **Images**: Extracted pictures and graphics
- **Tables**: Structured table data (JSON + Markdown)
- **Metadata**: Document properties and statistics

### ✅ Advanced Capabilities
- Document structure analysis
- Layout understanding
- Rich text formatting
- Table detection and extraction
- Image extraction with context
- Comprehensive metadata extraction

### ✅ Architecture Integration
- Implements `BaseExtractor` interface
- Compatible with `BenchmarkEngine`
- Integrated with `ExtractionService`
- Returns `ExtractionResult` with performance metrics
- No changes to existing architecture

---

## Installation

```bash
cd backend
pip install docling
```

The requirement is already added to `requirements.txt`:
```
docling>=1.0.0
```

---

## Implementation Details

### File Location
```
backend/app/extractors/docling_extractor.py
```

### Class Structure
```python
class DoclingExtractor(BaseExtractor):
    """Docling PDF extraction implementation."""
    
    def __init__(self):
        super().__init__("docling")
        self._docling_available = self._check_docling_installation()
    
    def extract(self, pdf_path: Path) -> ExtractionResult:
        """Legacy extraction method."""
        
    def extract_text(self, pdf_path: Path) -> str:
        """Full-featured extraction with all outputs."""
```

### Output Directory Structure
```
results/{timestamp}/docling/
├── markdown.md          # Markdown formatted text
├── document.json        # Complete document structure
├── metadata.json        # Document metadata
├── summary.json         # Extraction summary
├── images/              # Extracted images
│   ├── image_000.png
│   ├── image_001.png
│   └── ...
└── tables/              # Extracted tables
    ├── table_000.json
    ├── table_000.md
    ├── table_001.json
    ├── table_001.md
    └── ...
```

---

## Usage

### 1. Direct Usage
```python
from pathlib import Path
from app.extractors.docling_extractor import DoclingExtractor

extractor = DoclingExtractor()
text = extractor.extract_text(Path("document.pdf"))

# Outputs saved to: results/{timestamp}/docling/
print(f"Extracted {len(text)} characters")
```

### 2. With Benchmark Engine
```python
from app.benchmark.benchmark_engine import BenchmarkEngine
from app.extractors.docling_extractor import DoclingExtractor

engine = BenchmarkEngine()
extractor = DoclingExtractor()

result = engine.run_extraction(
    extraction_func=extractor.extract_text,
    pdf_path=Path("document.pdf"),
    library_name="docling",
)

print(f"Time: {result.execution_time_ms}ms")
print(f"Memory: {result.memory_usage_mb}MB")
print(f"CPU: {result.cpu_usage_percent}%")
```

### 3. Via API
```bash
POST /api/v1/extract
Content-Type: application/json

{
  "pdf_path": "./sample-pdfs/test.pdf",
  "libraries": ["docling"]
}
```

**Response:**
```json
{
  "benchmark_id": "20260715_103045_123",
  "pdf_path": "./sample-pdfs/test.pdf",
  "extraction_results": [{
    "library_name": "docling",
    "success": true,
    "execution_time_ms": 1234.56,
    "memory_usage_mb": 128.5,
    "cpu_usage_percent": 45.2,
    "text_content": "# Document Title\n\n...",
    "char_count": 5000,
    "word_count": 850,
    "pages_extracted": 10
  }]
}
```

### 4. Multi-Library Comparison
```bash
POST /api/v1/extract

{
  "pdf_path": "./sample-pdfs/test.pdf",
  "libraries": ["pypdf", "pdfplumber", "pymupdf", "docling"]
}
```

Compares all extractors and automatically identifies:
- Fastest library
- Most memory-efficient library
- Complete performance metrics

---

## Key Methods

### `extract_text(pdf_path: Path) -> str`
Primary extraction method that:
1. Validates PDF file
2. Checks Docling installation
3. Creates timestamped output directory
4. Converts PDF using Docling
5. Extracts markdown text
6. Saves all outputs (markdown, JSON, images, tables, metadata)
7. Returns markdown text

### `_create_output_directory(pdf_path: Path) -> Path`
Creates timestamped directory: `results/{timestamp}/docling/`

### `_save_outputs(...)`
Saves all extraction outputs:
- `markdown.md` - Markdown text
- `document.json` - JSON structure
- `metadata.json` - Document metadata
- `summary.json` - Extraction summary
- `images/` - Extracted images
- `tables/` - Extracted tables (JSON + MD)

### Error Handling
- Validates PDF before extraction
- Checks Docling installation
- Graceful error handling for missing outputs
- Detailed error logging
- Returns `ExtractionResult` with error details

---

## Integration

### ExtractionService
```python
# app/services/extraction_service.py

self._extractors: dict[str, BaseExtractor] = {
    "pypdf": PyPDFExtractor(),
    "pdfplumber": PDFPlumberExtractor(),
    "pymupdf": PyMuPDFExtractor(),
    "docling": DoclingExtractor(),  # ← Added
}
```

### LibraryService
```python
# app/services/library_service.py

AVAILABLE_LIBRARIES = {
    # ... other libraries ...
    "docling": {
        "display_name": "Docling",
        "module": "docling",
        "description": "Advanced document understanding and conversion library",
        "capabilities": [
            "text_extraction",
            "markdown_export",
            "json_export",
            "image_extraction",
            "table_extraction",
            "layout_analysis",
            "metadata_extraction",
        ],
        "performance_notes": "Comprehensive extraction with multiple output formats",
    },
}
```

---

## Output Files

### 1. markdown.md
Clean markdown formatted text with:
- Headings preserved
- Paragraphs formatted
- Lists maintained
- Table structures

### 2. document.json
Complete document structure:
```json
{
  "pages": [...],
  "elements": [...],
  "tables": [...],
  "images": [...]
}
```

### 3. metadata.json
Document metadata:
```json
{
  "source": "/path/to/document.pdf",
  "num_pages": 10,
  "extraction_time": "2026-07-15T10:30:45",
  "docling_version": "1.0.0",
  "document_metadata": {...}
}
```

### 4. summary.json
Extraction summary:
```json
{
  "extractor": "docling",
  "extraction_time": "2026-07-15T10:30:45",
  "statistics": {
    "text_length": 5000,
    "word_count": 850,
    "images_extracted": 3,
    "tables_extracted": 2,
    "pages": 10
  },
  "outputs": {
    "markdown": "markdown.md",
    "json": "document.json",
    "metadata": "metadata.json",
    "images": "images/ (3 files)",
    "tables": "tables/ (2 files)"
  }
}
```

### 5. images/
Extracted images saved as PNG:
- `image_000.png`
- `image_001.png`
- etc.

### 6. tables/
Extracted tables in dual format:
- `table_000.json` - Structured data
- `table_000.md` - Markdown format
- etc.

---

## Performance Characteristics

### Advantages
✅ **Comprehensive**: Multiple output formats  
✅ **Rich Metadata**: Detailed document information  
✅ **Structure Aware**: Understands document layout  
✅ **Multi-Format**: Markdown, JSON, images, tables  

### Trade-offs
⚠️ **Speed**: May be slower than PyMuPDF  
⚠️ **Memory**: Higher memory usage for complex documents  
⚠️ **Complexity**: More output files to manage  

### Best Use Cases
- Documents requiring multiple export formats
- Need for image and table extraction
- Structured data extraction
- Document analysis and conversion
- Comprehensive content preservation

---

## Comparison with Other Extractors

| Feature | PyPDF | PDFPlumber | PyMuPDF | Docling |
|---------|-------|------------|---------|---------|
| Text Extraction | ✓ | ✓ | ✓ | ✓ |
| Markdown Export | ✗ | ✗ | ✗ | ✓ |
| JSON Export | ✗ | ✗ | ✗ | ✓ |
| Image Extraction | ✗ | ✗ | ✓ | ✓ |
| Table Extraction | ✗ | ✓ | ✗ | ✓ |
| Layout Analysis | ✗ | ✓ | ✗ | ✓ |
| Speed | Medium | Medium | Fast | Medium |
| Memory Usage | Low | Medium | Low | High |

---

## Error Handling

### Installation Check
```python
if not self._docling_available:
    raise ImportError("Docling is not installed. Install with: pip install docling")
```

### PDF Validation
```python
# Uses BaseExtractor.validate_pdf()
if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

if not pdf_path.suffix.lower() == '.pdf':
    raise ValueError(f"Not a PDF file: {pdf_path}")
```

### Graceful Degradation
If saving outputs fails, extraction still succeeds:
```python
try:
    self._save_outputs(...)
except Exception as e:
    logger.error(f"Error saving outputs: {e}")
    # Don't raise - extraction succeeded
```

---

## Examples

See [examples/docling_usage.py](../examples/docling_usage.py) for:
1. Basic extraction
2. Benchmarked extraction
3. Multiple output formats
4. API usage
5. Multi-library comparison

---

## API Endpoints

### GET /api/v1/libraries
Returns Docling in the library list:
```json
{
  "libraries": [
    {
      "name": "docling",
      "display_name": "Docling",
      "description": "Advanced document understanding...",
      "is_installed": true,
      "capabilities": [
        "text_extraction",
        "markdown_export",
        "json_export",
        "image_extraction",
        "table_extraction"
      ]
    }
  ]
}
```

### POST /api/v1/extract
Accepts `"docling"` in libraries array:
```json
{
  "pdf_path": "./sample-pdfs/test.pdf",
  "libraries": ["docling"]
}
```

---

## Architecture Compliance

### ✅ No Breaking Changes
- Implements existing `BaseExtractor` interface
- Uses existing `BenchmarkEngine`
- Returns existing `ExtractionResult` model
- Integrates via existing `ExtractionService`
- Compatible with existing API endpoints

### ✅ Clean Architecture
- **Domain Layer**: Uses existing models
- **Application Layer**: Implements BaseExtractor
- **Infrastructure Layer**: Docling integration
- **Presentation Layer**: No changes needed

### ✅ SOLID Principles
- **Single Responsibility**: Extraction only
- **Open/Closed**: Extends BaseExtractor
- **Liskov Substitution**: Fully compatible
- **Interface Segregation**: Minimal interface
- **Dependency Inversion**: Depends on abstractions

---

## Testing

### Manual Test
```python
# Run example
python examples/docling_usage.py
```

### API Test
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test extraction
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "./sample-pdfs/test.pdf",
    "libraries": ["docling"]
  }'
```

### Verify Outputs
```bash
# Check output directory
ls -R results/*/docling/

# Should contain:
# - markdown.md
# - document.json
# - metadata.json
# - summary.json
# - images/ (if images found)
# - tables/ (if tables found)
```

---

## Troubleshooting

### Docling Not Installed
```
ImportError: Docling is not installed
```
**Solution:** `pip install docling`

### Missing Outputs
Some documents may not have images or tables:
```
images_extracted: 0
tables_extracted: 0
```
**This is normal** - not all PDFs contain images/tables.

### Memory Issues
Large PDFs may consume significant memory:
```
memory_usage_mb: 500.0
```
**Solution:** Process PDFs in batches or use pagination.

---

## Future Enhancements

Potential improvements:
- [ ] Async extraction for large documents
- [ ] Batch processing support
- [ ] Custom output format configuration
- [ ] Selective extraction (e.g., images only)
- [ ] Progress callbacks
- [ ] Streaming support

---

## References

- [Docling Documentation](https://github.com/docling)
- [BaseExtractor Interface](../app/extractors/base_extractor.py)
- [BenchmarkEngine](./BENCHMARK_ENGINE.md)
- [API Documentation](../README.md)

---

**Implementation Date:** 2026-07-15  
**Status:** ✅ Complete and Production-Ready  
**Maintainer:** PDF Extraction Benchmark Team
