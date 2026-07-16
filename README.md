# PDF Extraction Benchmark

A comprehensive monorepo application for benchmarking and comparing different PDF extraction methods. Built with Next.js 15 (frontend) and FastAPI (backend) following Clean Architecture and SOLID principles.

## 🎯 Overview

This application allows you to:
- Upload PDF documents
- Run extraction benchmarks with multiple methods
- Compare performance metrics (speed, memory, CPU usage)
- Visualize results with interactive charts
- Analyze accuracy and quality of extraction
- **Generate comprehensive markdown reports automatically** 📄

## 🏗️ Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│     Presentation Layer (API)        │
├─────────────────────────────────────┤
│     Application Layer (Use Cases)   │
├─────────────────────────────────────┤
│     Domain Layer (Business Logic)   │
├─────────────────────────────────────┤
│     Infrastructure Layer (External) │
└─────────────────────────────────────┘
```

### Project Structure

```
pdf-benchmark/
├── frontend/              # Next.js 15 Application
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React Components
│   │   ├── lib/          # Utilities & API Client
│   │   └── types/        # TypeScript Types
│   └── package.json
│
├── backend/              # FastAPI Application
│   ├── app/
│   │   ├── core/        # Configuration
│   │   ├── domain/      # Business Logic
│   │   ├── application/ # Use Cases
│   │   ├── infrastructure/ # External Concerns
│   │   └── presentation/   # API Endpoints
│   └── requirements.txt
│
├── results/              # Benchmark Results
├── sample-pdfs/          # Uploaded PDFs
├── logs/                 # Application Logs
└── docker-compose.yml    # Docker Configuration
```

## 🚀 Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - Component library
- **TanStack Query** - Data fetching and caching
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Backend
- **Python 3.12** - Programming language
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Loguru** - Logging
- **psutil** - System monitoring
- **python-multipart** - File uploads

### PDF Extraction Libraries
- **PyPDF** - Pure Python PDF library with good stability
- **PDFPlumber** - Powerful library for extracting text and tables
- **PyMuPDF** - Fast C-based library with extensive features
- **Docling** - Advanced document understanding and conversion library
  - Multiple output formats: Markdown, JSON
  - Image and table extraction
  - Rich metadata extraction
  - Layout analysis
- **MinerU** - High-quality PDF extraction with layout analysis and OCR
  - Advanced layout analysis
  - Automatic OCR fallback
  - Multiple output formats: Markdown, JSON
  - Image and table extraction
  - Optimized for complex layouts
- **Unstructured** - Universal document processing library
  - Element-based extraction
  - High-resolution strategy
  - Element type classification
  - Image and table extraction
  - Multiple output formats: Markdown, JSON
- **OpenDataLoader** - Unified data loading library
  - Document-based extraction
  - Metadata support
  - Image and table extraction
  - Multiple output formats: Markdown, JSON

## 📋 Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **npm or yarn**
- **Docker & Docker Compose** (optional)

## 🛠️ Installation

### Option 1: Local Development

#### 1. Clone the repository
```bash
cd c:\Projects\POC
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
copy .env.example .env
# Or on Linux/Mac: cp .env.example .env
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
copy .env.example .env.local
# Or on Linux/Mac: cp .env.example .env.local
```

### Option 2: Docker

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## 🎮 Running the Application

### Local Development

#### Start Backend (Terminal 1)
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Using Makefile (Unix/Linux/Mac)

```bash
# Install all dependencies
make install

# Run both servers
make dev

# Run backend only
make dev-backend

# Run frontend only
make dev-frontend

# Docker commands
make build   # Build images
make up      # Start containers
make down    # Stop containers

# Maintenance
make clean   # Clean build artifacts
make test    # Run tests
make lint    # Run linters
```

## � Automatic Report Generation

The system **automatically generates comprehensive markdown reports** after each benchmark execution. Reports are saved to `results/{timestamp}/report.md` and include:

### Report Sections

1. **📊 Overview**
   - Document information (name, size, pages)
   - Benchmark summary (libraries tested, success/failure counts)
   - Fastest library identification

2. **💻 Machine Information**
   - OS, architecture, processor
   - CPU cores, frequency, memory
   - Python version

3. **🔬 Benchmark Results**
   - Detailed metrics for each library
   - Execution time, memory usage, CPU usage
   - Output sizes (markdown, JSON, images, tables)

4. **⚖️ Performance Comparison**
   - Side-by-side comparison table
   - Category winners (fastest, least memory, least CPU, most complete)

5. **✅ ❌ Pros and Cons Analysis**
   - Strengths and weaknesses of each library
   - Performance characteristics
   - Feature availability

6. **💡 Recommendations**
   - Best library for speed
   - Best library for memory efficiency
   - Best library for feature completeness
   - Overall balanced recommendation
   - Use case specific suggestions (short/medium/large documents)
   - Special requirements (OCR, tables, images, structure)

### Usage Example

```python
from app.services.extraction_service import ExtractionService
from pathlib import Path

service = ExtractionService()

# Run benchmark with automatic report generation
results, report_path = service.run_benchmark_with_report(
    pdf_path=Path("data/sample.pdf"),
    library_names=["pypdf", "docling", "mineru"],
    output_dir=Path("results"),
)

print(f"Report generated: {report_path}")
# Output: Report generated: results/2026_07_15_143022/report.md
```

See **REPORT_GENERATION.md** for detailed documentation.

## �📡 API Endpoints

### Base URL: `http://localhost:8000/api/v1`

#### Health Check
```http
GET /health
```

#### System Information
```http
GET /health/system
```

#### Upload PDF
```http
POST /upload
Content-Type: multipart/form-data
```

#### Run Benchmark
```http
POST /benchmark
Content-Type: application/json

{
  "pdf_id": "uuid",
  "methods": ["pypdf", "pdfplumber", "pymupdf", "docling", "mineru", "unstructured", "opendataloader"],
  "options": {
    "extract_images": false,
    "extract_tables": true
  }
}
```

#### Get Benchmark Status
```http
GET /benchmark/{benchmark_id}
```

#### Get Results
```http
GET /results/{benchmark_id}
```

#### Get Benchmark Report
```http
GET /reports/{benchmark_id}
# Returns markdown report at: results/{timestamp}/report.md
```

#### List All Results
```http
GET /results?limit=10&offset=0
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Environment Variables

### Backend (.env)
```env
APP_NAME=PDF Benchmark API
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=./sample-pdfs
RESULTS_DIR=./results
LOGS_DIR=./logs
MAX_UPLOAD_SIZE_MB=50
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🏛️ Architecture Principles

### SOLID Principles

1. **Single Responsibility**: Each class/module has one reason to change
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable for their base types
4. **Interface Segregation**: Many specific interfaces over one general interface
5. **Dependency Inversion**: Depend on abstractions, not concretions

### Clean Architecture Benefits

- **Framework Independence**: Business logic doesn't depend on frameworks
- **Testability**: Easy to test without UI, database, or external services
- **UI Independence**: Can change UI without changing business rules
- **Database Independence**: Can swap databases without affecting business logic
- **External Agency Independence**: Business rules don't know about external systems

## 📊 Features Roadmap

### Phase 1: Project Setup ✅
- [x] Monorepo structure
- [x] Frontend configuration (Next.js 15)
- [x] Backend configuration (FastAPI)
- [x] Docker setup
- [x] Environment configuration
- [x] CORS configuration
- [x] Logging setup

### Phase 2: Core Infrastructure (Next)
- [ ] Health check endpoints
- [ ] API client layer
- [ ] Error handling
- [ ] Request logging
- [ ] Basic UI layout

### Phase 3: File Upload
- [ ] Upload endpoint
- [ ] File validation
- [ ] Storage service
- [ ] Upload UI component
- [ ] Progress tracking

### Phase 4: Benchmark Execution
- [ ] PDF extraction methods
- [ ] Resource monitoring
- [ ] Benchmark orchestration
- [ ] Real-time status updates
- [ ] Background job processing

### Phase 5: Results & Visualization
- [ ] Results storage
- [ ] Results API
- [ ] Results table
- [ ] Performance charts
- [ ] Comparison analytics

### Phase 6: Polish
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error boundaries
- [ ] Loading states
- [ ] Documentation

## 🐛 Troubleshooting

### Backend not starting?
- Check if port 8000 is available
- Verify Python version: `python --version` (should be 3.12+)
- Ensure all dependencies are installed: `pip list`
- Check logs in `logs/` directory

### Frontend not starting?
- Check if port 3000 is available
- Verify Node version: `node --version` (should be 20+)
- Clear cache: `rm -rf .next` and restart
- Reinstall dependencies: `rm -rf node_modules && npm install`

### CORS errors?
- Verify `CORS_ORIGINS` in backend `.env`
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Restart both servers after changing environment variables

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [TanStack Query Documentation](https://tanstack.com/query/latest)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is for demonstration purposes.

## 👥 Authors

- Senior Software Architect

## 🔗 Links

- Backend API Docs: http://localhost:8000/docs
- Frontend App: http://localhost:3000
- GitHub Repository: [Your Repository URL]

---

**Built with ❤️ using Clean Architecture and SOLID principles**
