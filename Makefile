.PHONY: help test lint format clean build up down logs ci

# Default target
help:
	@echo "═══════════════════════════════════════════════════"
	@echo "  AI Resume Screening - Makefile Commands"
	@echo "═══════════════════════════════════════════════════"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run all linting"
	@echo "  make format         - Auto-format all code"
	@echo "  make ci             - Run full CI pipeline"
	@echo ""
	@echo "🐳 Docker Services:"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View logs"
	@echo "  make build          - Build Docker images"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean          - Clean temp files"
	@echo ""

# Testing
test:
	@echo "🧪 Running all tests in Docker..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-test
	@docker-compose -f docker-compose.test.yml run --rm backend-test
	@echo "✅ All tests completed"

test-python:
	@echo "🐍 Running Python tests..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-test

test-node:
	@echo "🟢 Running Node.js tests..."
	@docker-compose -f docker-compose.test.yml run --rm backend-test

# Linting
lint:
	@echo "🔍 Running all linting in Docker..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-lint
	@docker-compose -f docker-compose.test.yml run --rm backend-lint
	@echo "✅ Linting completed"

lint-python:
	@echo "🐍 Running Python linting..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-lint

lint-node:
	@echo "🟢 Running Node.js linting..."
	@docker-compose -f docker-compose.test.yml run --rm backend-lint

# Formatting
format:
	@echo "💅 Formatting all code..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-format black .
	@docker-compose -f docker-compose.test.yml run --rm backend-format npm run format
	@echo "✅ Formatting completed"

format-python:
	@echo "🐍 Formatting Python code..."
	@docker-compose -f docker-compose.test.yml run --rm python-api-format black .

format-node:
	@echo "🟢 Formatting Node.js code..."
	@docker-compose -f docker-compose.test.yml run --rm backend-format npm run format

# CI Pipeline
ci:
	@echo "═══════════════════════════════════════════════════"
	@echo "  Running Full CI Pipeline"
	@echo "═══════════════════════════════════════════════════"
	@echo ""
	@echo "Step 1/3: Linting..."
	@make lint
	@echo ""
	@echo "Step 2/3: Testing..."
	@make test
	@echo ""
	@echo "Step 3/3: Building Docker images..."
	@docker-compose -f docker-compose.test.yml build
	@echo ""
	@echo "═══════════════════════════════════════════════════"
	@echo "  ✅ CI Pipeline Completed Successfully"
	@echo "═══════════════════════════════════════════════════"

# Docker operations
build:
	@echo "🐳 Building Docker images..."
	@docker-compose build

up:
	@echo "🚀 Starting services..."
	@docker-compose up -d
	@echo "✅ Services started"

down:
	@echo "🛑 Stopping services..."
	@docker-compose down
	@echo "✅ Services stopped"

logs:
	@docker-compose logs -f

# Cleanup
clean:
	@echo "🧹 Cleaning up temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf python-api/htmlcov 2>/dev/null || true
	@rm -rf node-resume/coverage 2>/dev/null || true
	@rm -rf python-api/.ipynb_checkpoints 2>/dev/null || true
	@echo "✅ Cleanup completed"
