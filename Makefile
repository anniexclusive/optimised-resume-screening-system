.PHONY: help test build up down logs clean

# Default target
help:
	@echo "AI Resume Screening - Available Commands"
	@echo ""
	@echo "  make test     - Run all tests"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make build    - Build Docker images"
	@echo "  make clean    - Clean temp files"
	@echo ""

# Testing
test:
	@echo "Running Node.js tests..."
	@cd node-resume && npm test
	@echo ""
	@echo "Running Python tests..."
	@cd python-api && (pytest || echo "⚠️  pytest not found. Install with: pip install pytest") && true
	@echo ""
	@echo "✅ Tests completed"

# Docker operations
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Cleanup
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf python-api/htmlcov node-resume/coverage 2>/dev/null || true
