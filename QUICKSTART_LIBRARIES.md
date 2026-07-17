# Quick Start Guide - PDF Processing Libraries

## 🚀 All Libraries Installed Successfully!

All requested PDF processing libraries have been installed and verified:

✅ **PyPDF** (v6.14.2)  
✅ **PDFPlumber** (v0.11.8)  
✅ **PyMuPDF** (v1.26.5)  
✅ **Docling** (v2.69.1)  
✅ **MinerU** (magic-pdf v0.6.1)  
✅ **Unstructured** (v0.18.3)  
✅ **CORS** configured for localhost:3000 and localhost:3001

❌ **OpenDataLoader** - Not available on PyPI (requires manual installation)

---

## 🔧 Quick Commands

### Start the Backend API

```bash
cd /Users/sonta/Learning/pdf-benchmark/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Or using the Makefile

```bash
cd /Users/sonta/Learning/pdf-benchmark
make backend
```

### Test Library Imports

```bash
cd backend
./venv/bin/python3 -c "
import pypdf
import pdfplumber
import pymupdf
import docling
import magic_pdf
import unstructured
print('All libraries imported successfully!')
"
```

---

## 📚 Library Usage Examples

### 1. PyPDF - Basic PDF Reading

```python
from pypdf import PdfReader

reader = PdfReader("sample.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
print(text)
```

### 2. PDFPlumber - Table Extraction

```python
import pdfplumber

with pdfplumber.open("sample.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        text = page.extract_text()
        print(f"Page {page.page_number}: {len(tables)} tables")
```

### 3. PyMuPDF - Fast Processing

```python
import pymupdf  # imports as 'fitz'

doc = pymupdf.open("sample.pdf")
for page in doc:
    text = page.get_text()
    print(text)
```

### 4. Docling - Document Understanding

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("sample.pdf")
print(result.document.export_to_dict())
```

### 5. MinerU - Advanced Extraction

```python
from magic_pdf.data.data_reader_writer import FileBasedDataReader, FileBasedDataWriter
from magic_pdf.pipe.UNIPipe import UNIPipe

# Process PDF with MinerU
# (See examples/mineru_usage.py for full implementation)
```

### 6. Unstructured - Multi-format Processing

```python
from unstructured.partition.auto import partition

elements = partition("sample.pdf")
for element in elements:
    print(f"{element.category}: {element.text}")
```

---

## 🌐 CORS Configuration

The backend is configured to accept requests from:

- `http://localhost:3000` (default frontend)
- `http://localhost:3001` (alternative port)

### Modify CORS Origins

Edit `/Users/sonta/Learning/pdf-benchmark/backend/.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://example.com
```

---

## 🧪 Test the Installation

### Quick Verification

```bash
cd /Users/sonta/Learning/pdf-benchmark/backend
./venv/bin/python3 << EOF
import sys
print('Python:', sys.version)
print()

libraries = ['pypdf', 'pdfplumber', 'pymupdf', 'docling', 'magic_pdf', 'unstructured']
for lib in libraries:
    try:
        __import__(lib)
        print(f'✓ {lib}')
    except:
        print(f'✗ {lib}')
EOF
```

### Run Example Scripts

```bash
cd backend

# Test Docling
python examples/docling_usage.py

# Test MinerU
python examples/mineru_usage.py

# Test Unstructured
python examples/unstructured_usage.py
```

### Test API Endpoints

```bash
# Start the server first
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, test the endpoints
curl http://localhost:8000/
curl http://localhost:8000/docs
```

---

## 🔍 Available API Endpoints

Once the server is running, visit:

- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/

### Example API Routes

```
GET  /                         - Welcome message
GET  /api/v1/health           - Health check
POST /api/v1/extract          - Extract text from PDF
POST /api/v1/benchmark        - Run benchmark on PDF
GET  /api/v1/benchmark/history - Get benchmark history
```

---

## 📁 Project Structure

```
backend/
├── venv/                      # Virtual environment (all libs installed here)
├── app/
│   ├── main.py               # FastAPI app with CORS configured
│   ├── core/
│   │   ├── cors.py          # CORS middleware setup ✅
│   │   └── config.py        # Configuration with CORS_ORIGINS
│   ├── extractors/           # PDF extraction implementations
│   └── api/                  # API routes
├── examples/                  # Usage examples for each library
├── sample-pdfs/              # Test PDF files
├── requirements.txt          # All dependencies ✅
└── .env                      # Environment config with CORS ✅
```

---

## 🐛 Troubleshooting

### Import Errors

If you get import errors, make sure you're using the virtual environment:

```bash
cd /Users/sonta/Learning/pdf-benchmark/backend
source venv/bin/activate
python your_script.py
```

### CORS Issues

If frontend can't connect:

1. Check `.env` file has correct origins
2. Verify server is running on port 8000
3. Check browser console for CORS errors
4. Ensure frontend is using correct API URL

### Library-Specific Issues

**MinerU (magic-pdf):**

- Older version installed (v0.6.1) due to dependencies
- Some newer features may not be available

**Unstructured:**

- Installed with `--no-compile` flag
- May have slightly slower import times
- All functionality works normally

**OpenDataLoader:**

- Not available on PyPI
- Install manually from source if needed: `pip install git+https://github.com/...`

---

## 📖 Documentation

- **Full Installation Details:** `LIBRARIES_INSTALLATION_STATUS.md`
- **Backend Architecture:** `backend/ARCHITECTURE.md`
- **API Documentation:** Start server and visit `/docs`
- **Benchmark Engine:** `backend/BENCHMARK_ENGINE.md`

---

## ✨ Ready to Use!

Your PDF benchmark system is now fully configured with:

- 6 PDF processing libraries installed
- CORS enabled for frontend communication
- FastAPI backend ready to serve
- Example scripts for each library

**Next steps:**

1. Start the backend: `cd backend && uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Visit http://localhost:3000 to use the benchmark interface
4. Test extraction with sample PDFs from `sample-pdfs/` directory

Enjoy benchmarking! 🎉
