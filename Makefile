.PHONY: help test lint build up down restart logs clean

# Default target
help:
	@echo "AI Resume Screening - Available Commands"
	@echo ""
	@echo "  make test     - Run all tests"
	@echo "  make lint     - Run linting"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Rebuild and restart all services"
	@echo "  make logs     - View logs"
	@echo "  make build    - Build Docker images"
	@echo "  make clean    - Clean temp files"
	@echo ""

# Testing (runs locally - requires dependencies installed)
test:
	@echo "Running Node.js tests..."
	@cd node-resume && npm test
	@echo ""
	@echo "Running Python tests..."
	@cd python-api && python3 -m pytest
	@echo ""
	@echo "✅ All tests completed"

# Linting
lint:
	@echo "Running Node.js linting..."
	@cd node-resume && npm run lint
	@echo ""
	@echo "Running Python linting..."
	@cd python-api && python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo ""
	@echo "✅ Linting completed"

# Docker operations
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	@echo "Stopping containers..."
	docker-compose down
	@echo "Building images..."
	docker-compose build
	@echo "Starting containers..."
	docker-compose up -d
	@echo "✅ Services restarted"

logs:
	docker-compose logs -f

# Cleanup
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf python-api/htmlcov node-resume/coverage 2>/dev/null || true
