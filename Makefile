ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: help install start stop restart clean test lint build docker-build docker-up docker-down logs setup

# Default target
.DEFAULT_GOAL := help

# Directory variables - using CURDIR (current directory where Makefile is located)
PROJECT_ROOT := $(CURDIR)
NODE_DIR := $(PROJECT_ROOT)/node-resume
CLIENT_DIR := $(NODE_DIR)/client
PYTHON_DIR := $(PROJECT_ROOT)/python-api

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Display this help message
	@echo "$(CYAN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "$(CYAN)Installing backend dependencies...$(NC)"
	cd $(NODE_DIR) && npm install
	@echo "$(CYAN)Installing frontend dependencies...$(NC)"
	cd $(CLIENT_DIR) && npm install
	@echo "$(CYAN)Installing Python dependencies...$(NC)"
	cd $(PYTHON_DIR) && (pip3 install -r requirements.txt || pip install -r requirements.txt)
	@echo "$(GREEN)All dependencies installed!$(NC)"

start-all: ## Start all services (backend, frontend, python-api)
	@echo "$(CYAN)Starting Python API...$(NC)"
	cd $(PYTHON_DIR) && python app.py &
	@echo "$(CYAN)Starting Node.js backend...$(NC)"
	cd $(NODE_DIR) && node app.js &
	@echo "$(CYAN)Starting React frontend...$(NC)"
	cd $(CLIENT_DIR) && npm start &
	@echo "$(GREEN)All services started!$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:3001$(NC)"
	@echo "$(YELLOW)Python API: http://localhost:5000$(NC)"

start-backend: ## Start only the backend service
	@echo "$(CYAN)Starting Node.js backend...$(NC)"
	cd $(NODE_DIR) && node app.js

start-frontend: ## Start only the frontend service
	@echo "$(CYAN)Starting React frontend...$(NC)"
	cd $(CLIENT_DIR) && npm start

start-python: ## Start only the Python API
	@echo "$(CYAN)Starting Python API...$(NC)"
	cd $(PYTHON_DIR) && python predictbert.py

stop: ## Stop all running services
	@echo "$(CYAN)Stopping all services...$(NC)"
	pkill -f "node app.js" || true
	pkill -f "npm start" || true
	pkill -f "predictbert.py" || true
	@echo "$(GREEN)All services stopped!$(NC)"

restart: stop start-all ## Restart all services

test: ## Run all tests
	@echo "$(CYAN)Running backend tests...$(NC)"
	cd $(NODE_DIR) && npm test || true
	@echo "$(CYAN)Running frontend tests...$(NC)"
	cd $(CLIENT_DIR) && npm test -- --watchAll=false || true
	@echo "$(CYAN)Running Python tests...$(NC)"
	cd $(PYTHON_DIR) && pytest || true

lint: ## Run linters on all code
	@echo "$(CYAN)Linting backend...$(NC)"
	cd $(NODE_DIR) && npm run lint || true
	@echo "$(CYAN)Linting frontend...$(NC)"
	cd $(CLIENT_DIR) && npm run lint || true
	@echo "$(CYAN)Linting Python code...$(NC)"
	cd $(PYTHON_DIR) && flake8 . || true

build: ## Build all components
	@echo "$(CYAN)Building frontend...$(NC)"
	cd $(CLIENT_DIR) && npm run build
	@echo "$(GREEN)Build complete!$(NC)"

docker-build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)Docker images built!$(NC)"

docker-up: ## Start services using Docker Compose
	@echo "$(CYAN)Starting services with Docker Compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	docker-compose ps

docker-down: ## Stop Docker Compose services
	@echo "$(CYAN)Stopping Docker Compose services...$(NC)"
	docker-compose down
	@echo "$(GREEN)Services stopped!$(NC)"

docker-restart: docker-down docker-up ## Restart Docker services

docker-logs: ## View Docker container logs
	docker-compose logs -f

clean: ## Clean build artifacts and dependencies
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	rm -rf $(NODE_DIR)/node_modules
	rm -rf $(CLIENT_DIR)/node_modules
	rm -rf $(CLIENT_DIR)/build
	find $(PYTHON_DIR) -type d -name __pycache__ -exec rm -rf {} + || true
	find $(PYTHON_DIR) -type f -name "*.pyc" -delete || true
	@echo "$(GREEN)Cleaned!$(NC)"

dev: ## Start all services in development mode
	@echo "$(CYAN)Starting development environment...$(NC)"
	make install
	make start-all

ci: ## Run CI pipeline locally
	@echo "$(CYAN)Running CI pipeline...$(NC)"
	make lint
	make test
	make build
	@echo "$(GREEN)CI pipeline complete!$(NC)"

logs: ## Show logs from all running processes
	@echo "$(CYAN)Showing logs...$(NC)"
	tail -f /tmp/resume-*.log || echo "No logs found"

health-check: ## Check if all services are running
	@echo "$(CYAN)Checking service health...$(NC)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Frontend is running$(NC)" || echo "$(RED)✗ Frontend is not running$(NC)"
	@curl -s http://localhost:3001/health > /dev/null && echo "$(GREEN)✓ Backend is running$(NC)" || echo "$(RED)✗ Backend is not running$(NC)"
	@curl -s http://localhost:5000/health > /dev/null && echo "$(GREEN)✓ Python API is running$(NC)" || echo "$(RED)✗ Python API is not running$(NC)"

setup: ## Run CI/CD setup script
	@echo "$(CYAN)Running CI/CD setup script...$(NC)"
	@chmod +x $(PROJECT_ROOT)/scripts/setup-cicd.sh
	@$(PROJECT_ROOT)/scripts/setup-cicd.sh
	@echo "$(GREEN)Setup complete!$(NC)"