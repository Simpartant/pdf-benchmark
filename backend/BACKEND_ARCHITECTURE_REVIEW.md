# Backend Architecture Review & Recommendations

## Date: 2026-07-15

This document outlines the backend architecture issues identified and recommendations for improvements.

---

## 🔴 Critical Issues Identified

### 1. Duplicate API Layers

**Problem:**
```
backend/app/
├── api/              # Old API layer
│   ├── dependencies.py
│   ├── routes.py
│   └── schemas.py
└── presentation/     # New API layer
    └── api/
        └── v1/
            ├── endpoints/
            └── schemas/
```

**Impact:**
- Two competing API implementations
- Code duplication
- Maintenance confusion
- Inconsistent endpoint behavior

**Recommendation:**
1. **Consolidate to single API layer** under `presentation/api/v1/`
2. Remove duplicate `app/api/` directory
3. Update all imports
4. Use FastAPI's dependency injection properly

---

### 2. Models in Wrong Layer

**Current Structure:**
```
backend/app/
├── models/              # ❌ Should not be here
│   ├── extraction_result.py
│   ├── benchmark_result.py
│   └── document.py
└── domain/
    └── entities/        # ✅ Models should be here
        └── __init__.py  # Empty!
```

**Violation:** Clean Architecture domain layer is empty

**Recommendation:**
```
backend/app/domain/
├── entities/
│   ├── extraction_result.py
│   ├── benchmark_result.py
│   ├── document.py
│   └── library.py
├── value_objects/
│   ├── file_size.py
│   └── benchmark_id.py
└── repositories/
    └── benchmark_repository.py  # Interface
```

---

### 3. Empty Clean Architecture Layers

**Current State:**
- `domain/entities/` - Empty
- `domain/repositories/` - Empty
- `domain/services/` - Empty
- `application/use_cases/` - Empty
- `application/dtos/` - Empty
- `infrastructure/repositories/` - Empty

**All business logic lives in `services/`!**

**Recommendation:**

Implement proper Clean Architecture:

```
domain/
├── entities/
│   ├── benchmark.py
│   ├── extraction.py
│   └── library.py
├── repositories/
│   ├── benchmark_repository.py  # Interface
│   └── library_repository.py    # Interface
└── services/
    └── benchmark_domain_service.py

application/
├── use_cases/
│   ├── run_benchmark_use_case.py
│   ├── get_results_use_case.py
│   └── list_history_use_case.py
└── dtos/
    ├── benchmark_request_dto.py
    └── benchmark_response_dto.py

infrastructure/
├── repositories/
│   ├── file_benchmark_repository.py  # Implementation
│   └── memory_library_repository.py  # Implementation
└── persistence/
    ├── json_storage.py
    └── database.py

presentation/
└── api/
    └── v1/
        ├── endpoints/
        │   ├── benchmarks.py
        │   ├── libraries.py
        │   └── results.py
        └── dependencies.py
```

---

### 4. Global Singleton Pattern

**Problem:**
```python
# api/dependencies.py
_library_service: LibraryService | None = None
_extraction_service: ExtractionService | None = None

def get_library_service() -> LibraryService:
    global _library_service
    if _library_service is None:
        _library_service = LibraryService()
    return _library_service
```

**Issues:**
- Global state
- Not thread-safe
- Hard to test
- Memory leaks possible

**Recommendation:**

Use FastAPI's dependency injection:

```python
from functools import lru_cache
from fastapi import Depends

@lru_cache()
def get_library_repository():
    return MemoryLibraryRepository()

@lru_cache()
def get_benchmark_repository():
    return FileBenchmarkRepository()

def get_library_service(
    repo: LibraryRepository = Depends(get_library_repository)
) -> LibraryService:
    return LibraryService(repo)

def get_run_benchmark_use_case(
    benchmark_repo: BenchmarkRepository = Depends(get_benchmark_repository),
    library_service: LibraryService = Depends(get_library_service)
) -> RunBenchmarkUseCase:
    return RunBenchmarkUseCase(benchmark_repo, library_service)
```

Or use `dependency-injector` library for more complex scenarios.

---

### 5. Broad Exception Handling

**Problem:**
```python
try:
    result = extract_pdf(pdf_path)
except Exception as e:  # ❌ Too broad!
    logger.error(f"Error: {e}")
```

**Issues:**
- Hides specific errors
- Catches system exceptions
- Poor debugging experience

**Recommendation:**
```python
# Define domain exceptions
class ExtractionError(Exception):
    pass

class LibraryNotFoundError(ExtractionError):
    pass

class InvalidPdfError(ExtractionError):
    pass

# Use specific exceptions
try:
    result = extract_pdf(pdf_path)
except InvalidPdfError as e:
    logger.warning(f"Invalid PDF: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except LibraryNotFoundError as e:
    logger.error(f"Library missing: {e}")
    raise HTTPException(status_code=500, detail=str(e))
except ExtractionError as e:
    logger.error(f"Extraction failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
# Let critical errors propagate
```

---

## 🟡 High Priority Improvements

### 6. Service Layer Refactoring

**Current:**
```python
class ExtractionService:
    def __init__(self):
        self._extractors = {
            "pypdf": PyPDFExtractor(),  # ❌ Direct instantiation
            "pdfplumber": PDFPlumberExtractor(),
        }
```

**Recommended:**
```python
class ExtractionService:
    def __init__(self, extractor_factory: ExtractorFactory):
        self._factory = extractor_factory

    def extract(self, library_name: str, pdf_path: Path):
        extractor = self._factory.create(library_name)
        return extractor.extract(pdf_path)

# Factory Pattern
class ExtractorFactory:
    def __init__(self):
        self._extractors = {}
    
    def register(self, name: str, extractor_class: Type[BaseExtractor]):
        self._extractors[name] = extractor_class
    
    def create(self, name: str) -> BaseExtractor:
        if name not in self._extractors:
            raise LibraryNotFoundError(f"Extractor not found: {name}")
        return self._extractors[name]()
```

---

### 7. Add Repository Pattern

**Recommendation:**
```python
# domain/repositories/benchmark_repository.py
from abc import ABC, abstractmethod

class BenchmarkRepository(ABC):
    @abstractmethod
    def save(self, benchmark: Benchmark) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, benchmark_id: str) -> Optional[Benchmark]:
        pass
    
    @abstractmethod
    def find_all(self, limit: int, offset: int) -> List[Benchmark]:
        pass

# infrastructure/repositories/file_benchmark_repository.py
class FileBenchmarkRepository(BenchmarkRepository):
    def __init__(self, storage_path: Path):
        self._storage_path = storage_path
    
    def save(self, benchmark: Benchmark) -> None:
        path = self._storage_path / f"{benchmark.id}.json"
        path.write_text(json.dumps(benchmark.to_dict()))
    
    # ... implement other methods
```

---

### 8. Implement Use Cases

**Recommendation:**
```python
# application/use_cases/run_benchmark_use_case.py
class RunBenchmarkUseCase:
    def __init__(
        self,
        benchmark_repo: BenchmarkRepository,
        extraction_service: ExtractionService,
        report_service: ReportService
    ):
        self._benchmark_repo = benchmark_repo
        self._extraction_service = extraction_service
        self._report_service = report_service
    
    def execute(self, request: RunBenchmarkRequest) -> RunBenchmarkResponse:
        # 1. Validate input
        self._validate_request(request)
        
        # 2. Create benchmark entity
        benchmark = Benchmark.create(
            pdf_path=request.pdf_path,
            libraries=request.libraries
        )
        
        # 3. Run extractions
        for library in request.libraries:
            result = self._extraction_service.extract(library, request.pdf_path)
            benchmark.add_result(result)
        
        # 4. Generate report
        if request.generate_report:
            report = self._report_service.generate(benchmark)
            benchmark.set_report(report)
        
        # 5. Save benchmark
        self._benchmark_repo.save(benchmark)
        
        # 6. Return response
        return RunBenchmarkResponse.from_benchmark(benchmark)
```

---

## 🟢 Medium Priority Improvements

### 9. Add Logging Middleware

```python
# presentation/middleware/logging_middleware.py
import time
from loguru import logger

async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} ({process_time:.3f}s)",
        extra={
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    return response
```

---

### 10. Add Pagination

```python
# application/dtos/pagination.py
from pydantic import BaseModel

class PaginationParams(BaseModel):
    limit: int = 10
    offset: int = 0
    
    @property
    def skip(self) -> int:
        return self.offset * self.limit

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        return cls(
            items=items,
            total=total,
            page=params.offset,
            page_size=params.limit,
            has_next=(params.offset + 1) * params.limit < total
        )

# Usage in endpoint
@router.get("/history")
async def get_history(
    pagination: PaginationParams = Depends(),
    use_case: GetHistoryUseCase = Depends()
) -> PaginatedResponse[BenchmarkMetadata]:
    return use_case.execute(pagination)
```

---

### 11. Add Caching

```python
from functools import lru_cache
from cachetools import TTLCache, cached

# Simple in-memory cache
library_cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes

@cached(cache=library_cache)
def get_library_status(library_name: str) -> LibraryStatus:
    # Expensive check
    return check_library_availability(library_name)
```

---

### 12. Add Request Validation

```python
# application/dtos/benchmark_request_dto.py
from pydantic import BaseModel, validator, Field

class RunBenchmarkRequest(BaseModel):
    pdf_path: str = Field(..., description="Path to PDF file")
    libraries: List[str] = Field(..., min_items=1, description="Libraries to test")
    options: Optional[BenchmarkOptions] = None
    
    @validator('pdf_path')
    def validate_pdf_path(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError("PDF file does not exist")
        if not path.suffix.lower() == '.pdf':
            raise ValueError("File must be a PDF")
        if path.stat().st_size > 50 * 1024 * 1024:  # 50MB
            raise ValueError("File size exceeds 50MB limit")
        return v
    
    @validator('libraries')
    def validate_libraries(cls, v):
        allowed = ["pypdf", "pdfplumber", "pymupdf", "docling", "mineru", "unstructured", "opendataloader"]
        invalid = [lib for lib in v if lib not in allowed]
        if invalid:
            raise ValueError(f"Invalid libraries: {', '.join(invalid)}")
        return v
```

---

## 📋 Implementation Priority

### Phase 1 (Week 1-2): Critical Architecture Fixes
1. ✅ Move models to domain/entities/
2. ✅ Remove duplicate API layer (api/ folder)
3. ✅ Implement repository pattern
4. ✅ Fix dependency injection

### Phase 2 (Week 3-4): Clean Architecture
5. ✅ Implement use cases
6. ✅ Add DTOs
7. ✅ Implement domain services
8. ✅ Add domain exceptions

### Phase 3 (Week 5-6): Production Features
9. ✅ Add pagination
10. ✅ Add caching
11. ✅ Improve logging
12. ✅ Add request validation

### Phase 4 (Week 7-8): Testing & Polish
13. ✅ Add unit tests
14. ✅ Add integration tests
15. ✅ Add API documentation
16. ✅ Performance optimization

---

## 📊 Expected Benefits

### Code Quality:
- Proper separation of concerns
- Testable components
- Clear dependencies
- Maintainable codebase

### Performance:
- Caching reduces redundant operations
- Pagination prevents memory issues
- Optimized database queries

### Maintainability:
- Easy to add new features
- Easy to modify existing features
- Clear structure
- Self-documenting code

### Reliability:
- Proper error handling
- Input validation
- Logging for debugging
- Graceful degradation

---

## 🎯 Success Metrics

- ✅ Zero global variables
- ✅ All domain entities in domain/ layer
- ✅ All business logic in use cases
- ✅ 100% type coverage with Pydantic
- ✅ All endpoints have tests
- ✅ Response time < 200ms (95th percentile)
- ✅ Zero broad exception handlers

---

## 📚 References

- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)
- FastAPI Best Practices
- Python Design Patterns
- SOLID Principles

---

## ✅ Conclusion

The backend requires significant refactoring to align with Clean Architecture principles. The current structure mixes concerns and violates several SOLID principles. Following the recommendations will result in a more maintainable, testable, and scalable application.

**Current Status:** Foundation in place, requires architectural refactoring
**Target Status:** Production-ready with Clean Architecture
