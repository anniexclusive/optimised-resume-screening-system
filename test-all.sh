#!/bin/bash
# Comprehensive Test Script for AI Resume Screening
# Runs all tests, linting, and code quality checks in Docker

set -e  # Exit on error

echo "======================================"
echo "AI Resume Screening - Quality Checks"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

run_check() {
    local name="$1"
    local command="$2"

    echo -e "${YELLOW}Running: $name${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ PASSED: $name${NC}"
        echo ""
    else
        echo -e "${RED}✗ FAILED: $name${NC}"
        echo ""
        FAILURES=$((FAILURES + 1))
    fi
}

# Build all test images first
echo -e "${YELLOW}Building Docker test images...${NC}"
docker-compose -f docker-compose.test.yml build

echo ""
echo "======================================"
echo "Python API - Quality Checks"
echo "======================================"
echo ""

# Python Linting
run_check "Python Linting (Flake8)" \
    "docker-compose -f docker-compose.test.yml run --rm python-api-lint"

# Python Code Formatting
run_check "Python Formatting Check (Black)" \
    "docker-compose -f docker-compose.test.yml run --rm python-api-format"

# Python Tests
run_check "Python Tests (PyTest)" \
    "docker-compose -f docker-compose.test.yml run --rm python-api-test"

echo ""
echo "======================================"
echo "Node.js Backend - Quality Checks"
echo "======================================"
echo ""

# Node.js Linting
run_check "Node.js Linting (ESLint)" \
    "docker-compose -f docker-compose.test.yml run --rm backend-lint"

# Node.js Formatting
run_check "Node.js Formatting Check (Prettier)" \
    "docker-compose -f docker-compose.test.yml run --rm backend-format"

# Node.js Tests
run_check "Node.js Tests (Jest)" \
    "docker-compose -f docker-compose.test.yml run --rm backend-test"

echo ""
echo "======================================"
echo "Summary"
echo "======================================"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILURES check(s) failed${NC}"
    exit 1
fi
