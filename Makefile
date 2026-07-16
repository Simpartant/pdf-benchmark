# Makefile for PDF Benchmark Project

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build up down clean test lint format

help:
	@echo "PDF Benchmark - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install all dependencies (backend + frontend)"
	@echo "  make install-backend  - Install backend Python dependencies"
	@echo "  make install-frontend - Install frontend Node dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Run both backend and frontend in dev mode"
	@echo "  make dev-backend      - Run backend development server"
	@echo "  make dev-frontend     - Run frontend development server"
	@echo ""
	@echo "Docker:"
	@echo "  make build            - Build Docker images"
	@echo "  make up               - Start Docker containers"
	@echo "  make down             - Stop Docker containers"
	@echo ""
	@echo "Maintenance:"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean build artifacts and caches"

# Installation
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development
dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Docker
build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

down:
	@echo "Stopping Docker containers..."
	docker-compose down

# Testing
test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend && npm test

# Code Quality
lint:
	@echo "Running linters..."
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	cd backend && black .
	cd frontend && npm run format

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	cd frontend && rm -rf .next node_modules
	@echo "Clean complete!"
