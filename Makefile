ifneq (,$(wildcard .env.local))
    include .env.local
    export
endif


# Define directories
FRONTEND_DIR=$(PROJECT_DIR)/node-resume/client
BACKEND_DIR=$(PROJECT_DIR)/node-resume
PYTHON_DIR=$(PROJECT_DIR)/python-api

# Install dependencies
.PHONY: build
build:
	cd $(FRONTEND_DIR) && npm install
	cd $(BACKEND_DIR) && npm install

# Commands to start each service
start-frontend:
	cd $(FRONTEND_DIR) && npm start

start-backend:
	cd $(BACKEND_DIR) && node app.js

start-python:
	cd $(PYTHON_DIR) && python main.py

# Use concurrently to run all services together
start-all:
	npx concurrently \
		"cd $(FRONTEND_DIR) && npm start" \
		"cd $(BACKEND_DIR) && node app.js" \
		"cd $(PYTHON_DIR) && python predictbert.py"

# Stop all running processes
.PHONY: stop
stop:
	pkill -f "node"
	pkill -f "react-scripts"
	pkill -f "python"

# Clean up node_modules (optional)
.PHONY: clean
clean:
	rm -rf $(BACKEND_DIR)/node_modules
	rm -rf $(FRONTEND_DIR)/node_modules

.PHONY: start-frontend start-backend start-python start-all
