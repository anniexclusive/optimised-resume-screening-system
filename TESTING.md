# Testing & Quality Assurance Guide

This document explains how to run tests, linting, and code quality checks for the AI Resume Screening project.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Tests in Docker](#running-tests-in-docker)
- [Individual Test Commands](#individual-test-commands)
- [CI/CD Integration](#cicd-integration)
- [Code Quality Standards](#code-quality-standards)

---

## Quick Start

### Run All Tests at Once

```bash
# Run all tests, linting, and quality checks
./test-all.sh
```

This script will:
1. Build all Docker test images
2. Run Python linting (Flake8)
3. Run Python formatting check (Black)
4. Run Python tests (PyTest with coverage)
5. Run Node.js linting (ESLint)
6. Run Node.js formatting check (Prettier)
7. Run Node.js tests (Jest with coverage)

---

## Running Tests in Docker

All tests run in Docker containers to ensure consistency across environments.

### Python API Tests

#### Run All Python Checks
```bash
docker-compose -f docker-compose.test.yml run --rm python-api-test
docker-compose -f docker-compose.test.yml run --rm python-api-lint
docker-compose -f docker-compose.test.yml run --rm python-api-format
```

#### Individual Python Commands
```bash
# Run tests with coverage
docker-compose -f docker-compose.test.yml run --rm python-api-test

# Run linting only
docker-compose -f docker-compose.test.yml run --rm python-api-lint

# Check code formatting
docker-compose -f docker-compose.test.yml run --rm python-api-format

# Auto-format Python code
docker-compose -f docker-compose.test.yml run --rm python-api-format black .
```

### Node.js Backend Tests

#### Run All Node.js Checks
```bash
docker-compose -f docker-compose.test.yml run --rm backend-test
docker-compose -f docker-compose.test.yml run --rm backend-lint
docker-compose -f docker-compose.test.yml run --rm backend-format
```

#### Individual Node.js Commands
```bash
# Run tests with coverage
docker-compose -f docker-compose.test.yml run --rm backend-test

# Run linting only
docker-compose -f docker-compose.test.yml run --rm backend-lint

# Auto-fix linting issues
docker-compose -f docker-compose.test.yml run --rm backend-lint npm run lint:fix

# Check code formatting
docker-compose -f docker-compose.test.yml run --rm backend-format

# Auto-format code
docker-compose -f docker-compose.test.yml run --rm backend-format npm run format
```

---

## Individual Test Commands

### Python API

#### Running Tests Locally (without Docker)
```bash
cd python-api

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v --cov=. --cov-report=term-missing

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check formatting
black --check --diff .

# Auto-format
black .
```

### Node.js Backend

#### Running Tests Locally (without Docker)
```bash
cd node-resume

# Install dependencies
npm install

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run linting
npm run lint

# Auto-fix linting
npm run lint:fix

# Check formatting
npm run format:check

# Auto-format
npm run format
```

---

## CI/CD Integration

The GitHub Actions workflow automatically runs all tests and quality checks on every push and pull request.

### CI/CD Workflow

Located at `.github/workflows/ci-cd.yml`, the workflow:

1. **Backend Tests**: Runs Node.js tests, linting, and build
2. **Frontend Tests**: Runs React tests, linting, and build
3. **Python API Tests**: Runs Python tests, linting, and coverage
4. **Security Scan**: Runs Trivy vulnerability scanner and npm audit

### Viewing CI/CD Results

1. Go to the **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. View logs for each job
4. Check test coverage reports

---

## Code Quality Standards

### Python Standards

#### Linting (Flake8)
- Max line length: 127 characters
- Max cyclomatic complexity: 10
- Follows PEP 8 style guide
- Configuration: `.flake8`

#### Formatting (Black)
- Line length: 127 characters
- Target: Python 3.9+
- Configuration: `pyproject.toml`

#### Testing (PyTest)
- Minimum coverage: 80% (recommended)
- Test discovery: `test_*.py` files
- Configuration: `pytest.ini`

### Node.js Standards

#### Linting (ESLint)
- Extends: `eslint:recommended`
- Environment: Node.js, ES2021
- Configuration: `.eslintrc.js`

#### Formatting (Prettier)
- Semi-colons: required
- Single quotes: preferred
- Print width: 100 characters
- Configuration: `.prettierrc.js`

#### Testing (Jest)
- Test files: `*.test.js`
- Configuration: `jest.config.js`

---

## Docker Test Infrastructure

### Test Images

#### Python API Test Image
- **File**: `python-api/Dockerfile.test`
- **Base**: `python:3.9-slim`
- **Includes**: pytest, flake8, black, coverage tools

#### Node.js Backend Test Image
- **File**: `node-resume/Dockerfile.test`
- **Base**: `node:18-alpine`
- **Includes**: All dev dependencies (ESLint, Prettier, Jest)

### Docker Compose Test Services

The `docker-compose.test.yml` file defines isolated test services:

- `python-api-test`: Runs Python tests with coverage
- `python-api-lint`: Runs Flake8 linting
- `python-api-format`: Checks Black formatting
- `backend-test`: Runs Jest tests with coverage
- `backend-lint`: Runs ESLint
- `backend-format`: Checks Prettier formatting

---

## Troubleshooting

### Tests Failing in Docker but Pass Locally

1. **Rebuild Docker images**:
   ```bash
   docker-compose -f docker-compose.test.yml build --no-cache
   ```

2. **Check for environment differences**:
   - Python version (should be 3.9)
   - Node version (should be 18)
   - Dependencies versions

### Linting Errors

#### Python
```bash
# Auto-fix most issues with Black
docker-compose -f docker-compose.test.yml run --rm python-api-format black .

# Then check remaining issues
docker-compose -f docker-compose.test.yml run --rm python-api-lint
```

#### Node.js
```bash
# Auto-fix most issues with ESLint
docker-compose -f docker-compose.test.yml run --rm backend-lint npm run lint:fix

# Auto-format with Prettier
docker-compose -f docker-compose.test.yml run --rm backend-format npm run format
```

### Coverage Too Low

1. Check uncovered lines in the coverage report
2. Add tests for uncovered code paths
3. Focus on critical business logic first

---

## Best Practices

### Writing Tests

#### Python
```python
# Use pytest fixtures
@pytest.fixture
def app():
    return create_app()

# Use markers for slow tests
@pytest.mark.slow
def test_bert_model_loading():
    pass

# Use parametrize for multiple test cases
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_function(input, expected):
    assert function(input) == expected
```

#### Node.js
```javascript
// Use describe blocks for organization
describe('ResumeService', () => {
  describe('screenResumes', () => {
    it('should validate input', () => {
      // Test code
    });
  });
});

// Mock external dependencies
jest.mock('../services/httpClient');

// Use async/await for async tests
it('should handle async operations', async () => {
  const result = await asyncFunction();
  expect(result).toBeDefined();
});
```

### Pre-Commit Checks

Before committing, always run:

```bash
# Quick check
./test-all.sh

# Or manually
docker-compose -f docker-compose.test.yml run --rm python-api-lint
docker-compose -f docker-compose.test.yml run --rm backend-lint
```

---

## Summary

- ✅ All tests run in isolated Docker containers
- ✅ Comprehensive linting and formatting checks
- ✅ Automated CI/CD integration
- ✅ Easy one-command execution with `./test-all.sh`
- ✅ Consistent environment across development and CI/CD

For questions or issues, please open a GitHub issue.
