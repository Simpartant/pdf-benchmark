# Testing the Real Backend API

## Quick Start

### 1. Start the Backend Server

```bash
cd backend

# Activate virtual environment (if not already activated)
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

### 2. Test the Endpoints

#### Option 1: Use the Test Script

```bash
cd backend
python examples/test_api_endpoints.py
```

This will:
- Test both `/health` and `/libraries` endpoints
- Display results in the console
- Save results to `api_test_results.json`

#### Option 2: Use cURL

**Test Health Endpoint:**
```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "pythonVersion": "3.12.0",
  "uptime": 123.45
}
```

**Test Libraries Endpoint:**
```bash
curl http://localhost:8000/api/v1/libraries
```

**Expected Response:**
```json
{
  "libraries": [
    {
      "name": "pypdf",
      "displayName": "PyPDF",
      "installed": true,
      "version": "3.17.0",
      "status": "available",
      "description": "Pure Python PDF library with good stability",
      "capabilities": ["text_extraction", "metadata"],
      "performanceNotes": "Good for simple PDFs, slower on complex layouts"
    },
    ...
  ],
  "total": 7
}
```

#### Option 3: Use Browser

1. Open http://localhost:8000/docs
2. Interactive Swagger UI will load
3. Click on `/api/v1/health` or `/api/v1/libraries`
4. Click "Try it out"
5. Click "Execute"

#### Option 4: Use Postman/Insomnia

**GET** `http://localhost:8000/api/v1/health`
**GET** `http://localhost:8000/api/v1/libraries`

---

## Endpoint Details

### GET /api/v1/health

Returns application health status and system information.

**Response Fields:**
- `status` - Always "ok" when running
- `version` - Application version
- `pythonVersion` - Python runtime version
- `uptime` - Uptime in seconds

### GET /api/v1/libraries

Returns information about all PDF extraction libraries.

**Response Fields:**
- `libraries` - Array of library objects
- `total` - Total number of libraries

**Each library object contains:**
- `name` - Library identifier (e.g., "pypdf")
- `displayName` - Human-readable name
- `installed` - Boolean indicating if installed
- `version` - Installed version or null
- `status` - "available", "not_installed", or "error"
- `description` - Library description
- `capabilities` - Array of capabilities
- `performanceNotes` - Performance information

---

## Verification

### Check What's Installed

The `/libraries` endpoint performs real detection. To verify:

1. Start the server
2. Call `/api/v1/libraries`
3. Check which libraries show `"installed": true`

### Install Missing Libraries

To install a library (e.g., Docling):

```bash
# Install Docling
pip install docling

# Restart server
# Call /api/v1/libraries again
# Docling should now show "installed": true
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: CORS errors from frontend

**Solution:** Make sure `CORS_ORIGINS` in `.env` includes your frontend URL:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Issue: Import errors

**Solution:** Make sure you're in the `backend` directory and virtual environment is activated:
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

## Next Steps

Once the backend is running and endpoints are working:

1. ✅ Test both endpoints
2. ✅ Verify library detection
3. ✅ Check response formats
4. 🔄 Integrate with frontend
5. 🔄 Remove mock data from frontend pages
6. 🔄 Use real API calls in frontend

---

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Production Deployment

For production deployment, use:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or use Docker:

```bash
docker-compose up -d
```
