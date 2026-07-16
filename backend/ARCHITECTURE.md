# Backend Architecture Documentation

## Overview

The backend has been restructured following **Clean Architecture** principles with clear separation of concerns and dependency injection throughout.

## 🏗️ Architecture Structure

```
backend/app/
├── api/                    # API Layer (new)
│   ├── routes.py          # API endpoints
│   ├── schemas.py         # Pydantic request/response models
│   └── dependencies.py    # Dependency injection
│
├── services/              # Application Services (new)
│   ├── library_service.py    # Library management
│   ├── extraction_service.py # Extraction coordination
│   └── history_service.py    # History management
│
├── extractors/            # Extraction Implementations (new)
│   ├── base_extractor.py     # Abstract base class
│   ├── pypdf_extractor.py    # PyPDF implementation
│   ├── pdfplumber_extractor.py # PDFPlumber implementation
│   └── pymupdf_extractor.py  # PyMuPDF implementation
│
├── benchmark/             # Benchmarking (new)
│   └── benchmark_service.py  # Benchmark orchestration
│
├── models/                # Domain Models (new)
│   ├── document.py           # PDFDocument entity
│   ├── extraction_result.py  # ExtractionResult entity
│   ├── benchmark_result.py   # BenchmarkResult entity
│   ├── library.py            # Library entity
│   └── history.py            # ExtractionHistory entity
│
├── utils/                 # Utilities (new)
│   ├── file_utils.py         # File operations
│   └── text_utils.py         # Text processing
│
├── core/                  # Core Configuration (existing)
│   ├── config.py
│   ├── logging.py
│   ├── cors.py
│   └── dependencies.py
│
└── main.py               # FastAPI application
```

---

## 📋 Models (Domain Entities)

### 1. PDFDocument
**Location:** `app/models/document.py`

**Purpose:** Represents a PDF document in the system

**Attributes:**
- `id: UUID` - Unique identifier
- `filename: str` - Original filename
- `file_path: str` - Path to file
- `size_bytes: int` - File size
- `uploaded_at: datetime` - Upload timestamp
- `status: DocumentStatus` - Processing status

**Methods:**
- `mark_processing()` - Mark as processing
- `mark_completed()` - Mark as completed
- `mark_error()` - Mark as error
- `to_dict()` - Convert to dictionary

---

### 2. ExtractionResult
**Location:** `app/models/extraction_result.py`

**Purpose:** Result of PDF text extraction

**Attributes:**
- `id: UUID` - Unique identifier
- `library_name: str` - Library used
- `success: bool` - Success status
- `text_content: str` - Extracted text
- `execution_time_ms: float` - Execution time
- `memory_usage_mb: float` - Memory used
- `cpu_usage_percent: float` - CPU usage
- `pages_extracted: int` - Number of pages
- `char_count: int` - Character count
- `word_count: int` - Word count
- `error_message: Optional[str]` - Error if failed
- `metadata: Dict[str, Any]` - Additional metadata
- `extracted_at: datetime` - Extraction timestamp

**Methods:**
- `to_dict()` - Convert to dictionary

---

### 3. BenchmarkResult
**Location:** `app/models/benchmark_result.py`

**Purpose:** Result of benchmarking multiple libraries

**Attributes:**
- `id: UUID` - Unique identifier
- `pdf_filename: str` - PDF filename
- `pdf_id: UUID` - Reference to PDF document
- `extraction_results: List[ExtractionResult]` - Results from each library
- `total_duration_ms: float` - Total time
- `fastest_library: Optional[str]` - Fastest library name
- `most_efficient_memory: Optional[str]` - Most memory efficient
- `most_text_extracted: Optional[str]` - Extracted most text
- `created_at: datetime` - Creation timestamp
- `metadata: Dict[str, Any]` - Additional metadata

**Methods:**
- `calculate_summary()` - Calculate summary statistics
- `to_dict()` - Convert to dictionary

---

### 4. Library
**Location:** `app/models/library.py`

**Purpose:** Information about extraction library

**Attributes:**
- `name: str` - Library identifier
- `display_name: str` - Display name
- `version: Optional[str]` - Version number
- `description: Optional[str]` - Description
- `status: LibraryStatus` - Availability status
- `capabilities: List[str]` - Features supported
- `performance_notes: Optional[str]` - Performance notes

**Methods:**
- `to_dict()` - Convert to dictionary

---

### 5. ExtractionHistory
**Location:** `app/models/history.py`

**Purpose:** Historical record of extractions

**Attributes:**
- `id: UUID` - Unique identifier
- `pdf_filename: str` - PDF filename
- `pdf_id: UUID` - Reference to PDF
- `libraries_used: List[str]` - Libraries used
- `total_duration_ms: float` - Total duration
- `success_count: int` - Successful extractions
- `failure_count: int` - Failed extractions
- `benchmark_result_id: UUID` - Reference to benchmark
- `created_at: datetime` - Creation timestamp

**Methods:**
- `to_dict()` - Convert to dictionary

---

## 🔌 BaseExtractor Abstract Class

**Location:** `app/extractors/base_extractor.py`

**Purpose:** Abstract base class for all PDF extractors

**Interface:**

```python
class BaseExtractor(ABC):
    def __init__(self, library_name: str)
    
    @abstractmethod
    def extract(self, pdf_path: Path) -> ExtractionResult:
        """Must be implemented by all extractors"""
        pass
    
    def validate_pdf(self, pdf_path: Path) -> None:
        """Validate PDF file exists and is valid"""
        pass
    
    def get_library_name(self) -> str:
        """Get library name"""
        pass
```

**Implementations:**
1. **PyPDFExtractor** - `app/extractors/pypdf_extractor.py`
2. **PDFPlumberExtractor** - `app/extractors/pdfplumber_extractor.py`
3. **PyMuPDFExtractor** - `app/extractors/pymupdf_extractor.py`

**Status:** Interface created, extraction logic not implemented (as requested)

---

## 🛠️ Services (Business Logic)

### 1. LibraryService
**Location:** `app/services/library_service.py`

**Purpose:** Manage PDF extraction libraries

**Methods:**
- `get_all_libraries()` - Get all library info
- `get_library_by_name(name)` - Get specific library
- `get_available_libraries()` - Get installed libraries only
- `clear_cache()` - Clear library cache

**Features:**
- Automatic library detection
- Version checking
- Status tracking (available/not_installed/error)
- Caching for performance

---

### 2. ExtractionService
**Location:** `app/services/extraction_service.py`

**Purpose:** Coordinate PDF extraction operations

**Methods:**
- `get_extractor(library_name)` - Get extractor instance
- `extract_with_library(pdf_path, library_name)` - Extract with one library
- `extract_with_multiple_libraries(pdf_path, library_names)` - Extract with multiple
- `get_available_extractors()` - List available extractors

**Features:**
- Extractor registry
- Error handling
- Logging
- Multiple library support

---

### 3. HistoryService
**Location:** `app/services/history_service.py`

**Purpose:** Manage extraction history

**Methods:**
- `add_history(benchmark_result)` - Add history record
- `get_all_history()` - Get all history
- `get_history_by_id(history_id)` - Get specific record
- `delete_history(history_id)` - Delete record

**Features:**
- JSON file storage
- Automatic serialization/deserialization
- CRUD operations

---

### 4. BenchmarkService
**Location:** `app/benchmark/benchmark_service.py`

**Purpose:** Run and manage benchmarks

**Constructor:** Uses dependency injection
```python
def __init__(
    self,
    extraction_service: ExtractionService,
    history_service: HistoryService,
):
```

**Methods:**
- `run_benchmark(pdf_document, library_names)` - Run benchmark
- `run_benchmark_by_path(pdf_path, library_names)` - Run from path

**Features:**
- Multi-library benchmarking
- Automatic summary calculation
- History tracking
- Performance metrics

---

## 🌐 API Endpoints

### 1. GET /api/v1/health
**Purpose:** Health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-07-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

### 2. GET /api/v1/libraries
**Purpose:** Get all available extraction libraries

**Response:**
```json
{
  "libraries": [
    {
      "name": "pypdf",
      "display_name": "PyPDF",
      "version": "3.0.0",
      "description": "Pure Python PDF library...",
      "status": "available",
      "capabilities": ["text_extraction", "metadata"],
      "performance_notes": "Good for simple PDFs..."
    }
  ],
  "total": 3
}
```

**Features:**
- Shows installation status
- Version information
- Capabilities
- Performance notes

---

### 3. POST /api/v1/extract
**Purpose:** Extract text from PDF with benchmarking

**Request:**
```json
{
  "pdf_path": "/path/to/file.pdf",
  "libraries": ["pypdf", "pdfplumber", "pymupdf"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "pdf_filename": "file.pdf",
  "pdf_id": "uuid",
  "extraction_results": [
    {
      "id": "uuid",
      "library_name": "pypdf",
      "success": false,
      "text_content": "",
      "execution_time_ms": 0.0,
      "memory_usage_mb": 0.0,
      "cpu_usage_percent": 0.0,
      "pages_extracted": 0,
      "char_count": 0,
      "word_count": 0,
      "error_message": "Extraction not implemented yet",
      "extracted_at": "2026-07-15T10:30:00Z"
    }
  ],
  "total_duration_ms": 0.0,
  "fastest_library": null,
  "most_efficient_memory": null,
  "most_text_extracted": null,
  "created_at": "2026-07-15T10:30:00Z"
}
```

**Features:**
- Multi-library extraction
- Performance benchmarking
- Automatic history tracking
- Error handling
- Summary statistics

---

### 4. GET /api/v1/history
**Purpose:** Get extraction history

**Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "pdf_filename": "file.pdf",
      "pdf_id": "uuid",
      "libraries_used": ["pypdf", "pdfplumber"],
      "total_duration_ms": 1250.5,
      "success_count": 1,
      "failure_count": 1,
      "benchmark_result_id": "uuid",
      "created_at": "2026-07-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Features:**
- Lists all historical extractions
- Shows success/failure counts
- Duration tracking
- Sortable by date

---

### 5. DELETE /api/v1/history/{id}
**Purpose:** Delete history record

**Response:**
```json
{
  "success": true,
  "message": "History record {id} deleted successfully"
}
```

**Error Response (404):**
```json
{
  "detail": "History record not found: {id}"
}
```

---

## 💉 Dependency Injection

**Location:** `app/api/dependencies.py`

**Pattern:** Singleton services with FastAPI dependency injection

**Services:**
```python
LibraryServiceDep = Annotated[LibraryService, Depends(get_library_service)]
ExtractionServiceDep = Annotated[ExtractionService, Depends(get_extraction_service)]
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
BenchmarkServiceDep = Annotated[BenchmarkService, Depends(get_benchmark_service)]
```

**Usage in Endpoints:**
```python
@router.get("/libraries")
async def get_libraries(
    library_service: LibraryServiceDep,
) -> LibrariesResponse:
    # Use library_service
    pass
```

**Benefits:**
- Loose coupling
- Easy testing (can inject mocks)
- Singleton pattern for efficiency
- Automatic dependency resolution

---

## 🔧 Utilities

### File Utils (`app/utils/file_utils.py`)
- `is_pdf_file(file_path)` - Validate PDF file
- `get_file_size_mb(file_path)` - Get file size
- `ensure_directory(directory)` - Create directory
- `sanitize_filename(filename)` - Clean filename

### Text Utils (`app/utils/text_utils.py`)
- `count_words(text)` - Count words
- `count_characters(text)` - Count characters
- `extract_text_stats(text)` - Get text statistics
- `clean_text(text)` - Clean extracted text

---

## 📊 Architecture Principles Applied

### Clean Architecture ✅
- **Domain Layer**: Models, BaseExtractor
- **Application Layer**: Services, BenchmarkService
- **Infrastructure Layer**: Extractors, HistoryService (file storage)
- **Presentation Layer**: API routes, schemas

### SOLID Principles ✅

1. **Single Responsibility**: Each service has one clear purpose
2. **Open/Closed**: BaseExtractor allows new extractors without modifying code
3. **Liskov Substitution**: All extractors can be used interchangeably
4. **Interface Segregation**: Services have focused interfaces
5. **Dependency Inversion**: Services depend on abstractions (BaseExtractor)

### Dependency Injection ✅
- All services use constructor injection
- FastAPI Depends() for automatic injection
- Singleton pattern for efficiency
- Easy to test and mock

---

## 🎯 Current Status

### ✅ Implemented
- All domain models with proper methods
- BaseExtractor abstract class
- 3 extractor implementations (interfaces only)
- 4 services with business logic
- 5 API endpoints with full documentation
- Dependency injection throughout
- Pydantic schemas for API contracts
- Utility functions for common operations

### ⚠️ Not Implemented (As Requested)
- Actual PDF extraction logic in extractors
- Performance monitoring during extraction
- File upload handling

### 🚀 Ready For
- Implementing actual extraction logic in each extractor
- Adding performance metrics collection
- Adding file upload endpoint
- Adding authentication if needed
- Adding database instead of file storage

---

## 📖 Usage Example

```python
# 1. Check available libraries
GET /api/v1/libraries

# 2. Extract from PDF
POST /api/v1/extract
{
  "pdf_path": "./sample-pdfs/test.pdf",
  "libraries": ["pypdf", "pdfplumber", "pymupdf"]
}

# 3. View history
GET /api/v1/history

# 4. Delete history record
DELETE /api/v1/history/{uuid}
```

---

## 🔍 Testing the API

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All endpoints are documented and can be tested interactively.

---

**Architecture Created:** 2026-07-15  
**Status:** Complete - Ready for extraction implementation
