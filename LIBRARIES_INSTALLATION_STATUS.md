# PDF Processing Libraries - Installation Status

**Date:** July 16, 2026  
**Python Version:** 3.9.6  
**Virtual Environment:** `/Users/sonta/Learning/pdf-benchmark/backend/venv`

## ✅ Successfully Installed Libraries

### 1. **PyPDF** (v6.14.2)

- **Status:** ✅ Installed
- **Package:** `pypdf`
- **Purpose:** Basic PDF reading and manipulation
- **Use Case:** Text extraction, PDF merging/splitting

### 2. **PDFPlumber** (v0.11.8)

- **Status:** ✅ Installed
- **Package:** `pdfplumber`
- **Purpose:** Detailed PDF data extraction with layout analysis
- **Use Case:** Table extraction, precise text positioning

### 3. **PyMuPDF** (v1.26.5)

- **Status:** ✅ Installed
- **Package:** `pymupdf` (fitz)
- **Purpose:** Fast PDF rendering and manipulation
- **Use Case:** High-performance text/image extraction, rendering

### 4. **Docling** (v2.69.1)

- **Status:** ✅ Installed
- **Package:** `docling`
- **Purpose:** IBM's document understanding framework
- **Use Case:** Advanced document analysis, structure recognition

### 5. **MinerU** (v0.6.1)

- **Status:** ✅ Installed
- **Package:** `magic-pdf`
- **Purpose:** Advanced PDF extraction with AI capabilities
- **Use Case:** Complex layout extraction, scientific documents
- **Note:** Installed without full extras due to dependency resolution

### 6. **Unstructured** (v0.18.3)

- **Status:** ✅ Installed
- **Package:** `unstructured`
- **Purpose:** Universal document processing framework
- **Use Case:** Multi-format document processing, chunking for RAG
- **Note:** Installed with `--no-compile` flag due to Python 3.9 compatibility with olefile

## ❌ Not Installed

### OpenDataLoader

- **Status:** ❌ Not available on PyPI
- **Issue:** Package not published to PyPI
- **Alternative:** Manual installation from source if needed

## 🔧 CORS Configuration

### Status: ✅ Configured

**File:** `/Users/sonta/Learning/pdf-benchmark/backend/.env`

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Implementation:** `/Users/sonta/Learning/pdf-benchmark/backend/app/core/cors.py`

The CORS middleware is configured to:

- Allow origins from both ports 3000 and 3001
- Allow all methods (GET, POST, PUT, DELETE, etc.)
- Allow all headers
- Allow credentials
- Expose all headers
- Cache preflight requests for 3600 seconds

## 📦 Installation Summary

### Requirements File Updated

**File:** `/Users/sonta/Learning/pdf-benchmark/backend/requirements.txt`

```txt
# PDF Processing Libraries
pypdf>=6.0.0
pdfplumber>=0.11.0
pymupdf>=1.24.0
docling>=1.0.0
magic-pdf[full]>=0.7.0
unstructured[pdf]>=0.10.0
```

### Installation Commands Used

```bash
# Navigate to backend directory
cd /Users/sonta/Learning/pdf-benchmark/backend

# Install MinerU (magic-pdf)
./venv/bin/pip install 'magic-pdf[full]'

# Install Unstructured (with workaround for Python 3.9)
PYTHONDONTWRITEBYTECODE=1 ./venv/bin/pip install --no-compile unstructured
```

## ⚠️ Known Issues

### 1. Olefile Compatibility

- **Issue:** The `olefile` package (v0.47) contains Python 2 syntax incompatible with Python 3.9
- **Impact:** Cannot compile `.pyc` files for this package
- **Workaround:** Installed with `--no-compile` flag
- **Effect:** Package works but may have slightly slower import times

### 2. MinerU Version

- **Installed:** v0.6.1
- **Latest:** v1.3.0 was attempted but had dependency conflicts
- **Reason:** PyPI dependency resolver selected older version for compatibility
- **Impact:** Some newer features may not be available

## 🧪 Verification

All libraries were verified to import successfully:

```python
import pypdf          # ✓
import pdfplumber     # ✓
import pymupdf        # ✓
import docling        # ✓
import magic_pdf      # ✓
import unstructured   # ✓
```

## 📝 Next Steps

1. **Test each library** with sample PDFs from `sample-pdfs/` directory
2. **Update benchmark tests** to include all libraries
3. **Document API endpoints** for each extraction method
4. **Add error handling** for library-specific issues
5. **Create performance comparison** across all libraries

## 🔗 Related Files

- Backend requirements: `backend/requirements.txt`
- CORS configuration: `backend/app/core/cors.py`
- Environment config: `backend/.env`
- Main application: `backend/app/main.py`

## 📚 Documentation Links

- PyPDF: https://pypdf.readthedocs.io/
- PDFPlumber: https://github.com/jsvine/pdfplumber
- PyMuPDF: https://pymupdf.readthedocs.io/
- Docling: https://github.com/DS4SD/docling
- MinerU: https://github.com/opendatalab/MinerU
- Unstructured: https://github.com/Unstructured-IO/unstructured
