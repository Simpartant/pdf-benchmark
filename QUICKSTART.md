# Quick Start Guide

## ✅ Frontend Status: RUNNING

The frontend is successfully running on **http://localhost:3000**

## ⚙️ Backend Setup Required

Python was not found in your system PATH. To run the backend:

### Option 1: Install Python 3.12+

1. **Download Python 3.12+** from [python.org](https://www.python.org/downloads/)
2. **During installation, check "Add Python to PATH"**
3. Restart your terminal
4. Verify: `python --version` or `python3 --version`

### Option 2: Use Existing Python Installation

If Python is already installed but not in PATH:

```powershell
# Find Python installation
where.exe python
# Or
Get-Command python -ErrorAction SilentlyContinue
```

### Starting the Backend (After Python is installed)

```powershell
# Navigate to backend directory
cd c:\Projects\POC\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/redoc

## 🐳 Alternative: Use Docker

If you have Docker installed:

```powershell
# From project root
cd c:\Projects\POC

# Build and start both services
docker-compose up --build

# Or run in background
docker-compose up -d

# Stop services
docker-compose down
```

## 📊 Verifying the Setup

### Frontend Verification
- Open http://localhost:3000 in your browser
- You should see the "PDF Extraction Benchmark" home page
- Navigation links for Benchmark and Results should be visible

### Backend Verification (Once running)
- Open http://localhost:8000/docs
- Try the `/api/v1/health` endpoint
- Should return: `{"status": "healthy", "timestamp": "...", "version": "1.0.0"}`

## 📁 Project Structure Created

```
pdf-benchmark/
├── frontend/          ✅ Configured & Running
├── backend/           ⚠️  Needs Python installation
├── results/           ✅ Created
├── sample-pdfs/       ✅ Created
├── logs/              ✅ Created
├── docker-compose.yml ✅ Ready
├── Makefile          ✅ Ready
└── README.md         ✅ Complete documentation
```

## 🎯 Next Steps

1. **Install Python 3.12+** (if not already installed)
2. **Start the backend** following the steps above
3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
4. **Begin implementing features** from Phase 2 of the roadmap

## 🔧 Troubleshooting

### Port Already in Use

**Frontend (port 3000):**
```powershell
# Find process using port 3000
netstat -ano | findstr :3000
# Kill process by PID
taskkill /PID <PID> /F
```

**Backend (port 8000):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process by PID
taskkill /PID <PID> /F
```

### Module Not Found Errors

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation

- Full README: [README.md](./README.md)
- Backend API Docs: http://localhost:8000/docs (when running)
- Frontend Routes:
  - Home: http://localhost:3000
  - Benchmark: http://localhost:3000/benchmark
  - Results: http://localhost:3000/results

---

**Phase 1 Complete!** 🎉

Both frontend and backend are configured with clean architecture.
Ready for Phase 2 implementation.
