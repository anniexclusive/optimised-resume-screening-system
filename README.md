# AI Resume Screening System

An enterprise-grade AI-powered resume screening system that uses BERT-based natural language processing to automate resume evaluation. Built with SOLID design principles, comprehensive testing, and production-ready architecture.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Development](#development)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Functionality
- **AI-Powered Screening**: BERT-based semantic similarity analysis
- **Multi-Factor Scoring**: Skills (40%), Experience (30%), Education (20%), General Match (10%)
- **Batch Processing**: Upload and screen multiple resumes simultaneously
- **Explainable Results**: Human-readable explanations for each score
- **PDF Support**: Automatic text extraction from PDF resumes

### Technical Features
- **SOLID Architecture**: Single Responsibility, Dependency Injection, Clean Abstractions
- **87.65% Test Coverage**: Comprehensive unit and integration tests
- **Configuration-Driven**: Externalized configuration via environment variables
- **Docker Support**: Full containerization with Docker Compose
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Performance Optimized**: Session caching, parallel processing, efficient model loading

---

## Architecture

The system follows a **microservices architecture** with clear separation of concerns:

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
└────────┬────────┘
         │
┌────────▼─────────┐
│  Nginx Proxy     │  (Port 80)
└─────────┬────────┘
          │
     ┌────┴─────┐
     │          │
┌────▼────┐  ┌─▼─────────┐
│ Node.js │──│  Python   │
│ Backend │  │ AI Service│
│(Port    │  │(Port 5000)│
│ 3001)   │  │           │
└─────────┘  └───────────┘
```

**For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)**

### Key Design Patterns

- **Service Layer Pattern**: Business logic separated into dedicated services
- **Dependency Injection**: Services receive dependencies via constructor
- **Singleton Pattern**: Single BERT model instance shared across requests
- **Factory Pattern**: Configuration-based service instantiation
- **Repository Pattern**: Abstracted data access (future enhancement)

---

## Technology Stack

### Frontend
- **React** 19.0 - Modern UI framework
- **React Router** 6.30 - Client-side routing
- **Axios** - HTTP client

### Backend (Node.js)
- **Express** 4.21 - Web framework
- **Multer** 2.0 - File upload handling
- **Axios** 1.8 - HTTP client for Python API
- **FormData** 4.0 - Multipart form data handling

### AI Service (Python)
- **Flask** 2.0 - Web framework
- **Sentence Transformers** 3.3 - BERT embeddings
- **PyTorch** 2.6 - Deep learning framework
- **PyPDF2** 3.0 - PDF text extraction
- **NumPy** 1.24 - Numerical computing

### Testing
- **Jest** 29.7 - Node.js testing framework (87.65% coverage)
- **Pytest** 7.4 - Python testing framework
- **Pytest-xdist** - Parallel test execution
- **Supertest** 6.3 - API endpoint testing

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **Nginx** - Reverse proxy and load balancing
- **GitHub Actions** - CI/CD pipeline

---

## Prerequisites

### Required Software
- **Node.js** 18.x or higher
- **Python** 3.9 or higher
- **npm** 8.x or higher
- **Docker** & **Docker Compose** (for containerized deployment)

### Optional
- **Make** (for Makefile commands)
- **Git** (for version control)

---

## Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/ai-resume-screening.git
cd ai-resume-screening

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# The application is now available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:3001
# Python API: http://localhost:5000
# Nginx: http://localhost:80
```

### Option 2: Local Development

#### 1. Install Node.js Backend Dependencies

```bash
cd node-resume
npm install
```

#### 2. Install Python API Dependencies

```bash
cd python-api
pip install -r requirements.txt
```

#### 3. Install Frontend Dependencies

```bash
cd node-resume/client
npm install
```

---

## Configuration

### Environment Variables

The system uses environment variables for configuration following the [12-Factor App](https://12factor.net/) methodology.

#### Node.js Backend (.env)

Create `node-resume/.env`:

```bash
# Server Configuration
NODE_ENV=development
PORT=3001
HOST=localhost

# Python API Configuration
PYTHON_API_URL=http://localhost:5000
API_TIMEOUT=30000

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES=10

# CORS Configuration
CORS_ORIGIN=http://localhost:3000
```

#### Python API (.env)

Create `python-api/.env`:

```bash
# Flask Configuration
FLASK_PORT=5000
FLASK_DEBUG=false

# BERT Model Configuration
BERT_MODEL=all-MiniLM-L6-v2
MODEL_CACHE_DIR=./models
DEVICE=cpu
MAX_SEQ_LENGTH=256

# Scoring Weights (must sum to 1.0)
WEIGHT_GENERAL=0.10
WEIGHT_SKILLS=0.40
WEIGHT_EXPERIENCE=0.30
WEIGHT_EDUCATION=0.20

# Model Loading
LAZY_LOAD=false
SHOW_PROGRESS=true
LOCAL_FILES_ONLY=false
```

### Configuration Files

All configuration is centralized in dedicated config files:

- **Node.js**: `node-resume/config/api.config.js`
- **Python Model**: `python-api/config/model_config.py`
- **Python Scoring**: `python-api/config/scoring_config.py`

**See [ARCHITECTURE.md - Configuration Management](ARCHITECTURE.md#configuration-management) for details**

---

## Running the Application

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Using Make Commands

```bash
# Start all services
make start-all

# Stop all services
make stop-all

# View logs
make logs
```

### Manual Local Development

#### Terminal 1: Python API
```bash
cd python-api
python app.py
# Running on http://localhost:5000
```

#### Terminal 2: Node.js Backend
```bash
cd node-resume
npm start
# Running on http://localhost:3001
```

#### Terminal 3: React Frontend
```bash
cd node-resume/client
npm start
# Running on http://localhost:3000
```

**Access the application at [http://localhost:3000](http://localhost:3000)**

---

## Testing

### Node.js Backend Tests

```bash
cd node-resume

# Run all tests
npm test

# Run with coverage report
npm test -- --coverage

# Run specific test file
npm test -- tests/httpClient.test.js

# Watch mode for development
npm run test:watch
```

**Current Coverage: 87.65%** (exceeds 80% target)

### Python API Tests

```bash
cd python-api

# Run all tests (parallel execution)
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_scoring.py

# Run only unit tests (fast)
pytest -m unit

# Run slow tests (BERT model tests)
pytest -m slow
```

### Integration Tests

```bash
cd node-resume

# Run integration tests (requires Python API running)
npm test -- tests/integration/
```

**See [docs/solid-refactoring/04-PHASE4-TESTING-SUMMARY.md](docs/solid-refactoring/04-PHASE4-TESTING-SUMMARY.md) for detailed test documentation**

---

## Project Structure

```
ai-resume-screening/
├── node-resume/              # Node.js Backend
│   ├── config/               # Configuration files
│   │   └── api.config.js     # Centralized API config
│   ├── services/             # Service layer (SOLID)
│   │   ├── httpClient.js     # HTTP abstraction
│   │   ├── fileService.js    # File operations
│   │   ├── resumeService.js  # Business logic
│   │   └── index.js          # Service exports
│   ├── tests/                # Unit tests
│   │   ├── httpClient.test.js
│   │   ├── fileService.test.js
│   │   ├── resumeService.test.js
│   │   └── integration/      # Integration tests
│   ├── __mocks__/            # Custom mocks for testing
│   ├── uploads/              # Temporary file storage
│   ├── app.js                # Express application
│   ├── jest.config.js        # Jest configuration
│   ├── package.json
│   └── client/               # React Frontend
│       ├── src/
│       ├── public/
│       └── package.json
│
├── python-api/               # Python AI Service
│   ├── config/               # Configuration modules
│   │   ├── model_config.py   # BERT model config
│   │   └── scoring_config.py # Scoring weights config
│   ├── services/             # Service layer
│   │   └── similarityService.py # BERT similarity
│   ├── utils/                # Utility functions
│   │   └── scoring.py        # Scoring logic
│   ├── tests/                # Unit tests
│   │   ├── test_config.py
│   │   ├── test_scoring.py
│   │   ├── test_similarity_service.py
│   │   ├── test_api.py
│   │   └── conftest.py       # Test fixtures
│   ├── app.py                # Flask application
│   ├── pytest.ini            # Pytest configuration
│   └── requirements.txt
│
├── nginx/                    # Nginx configuration
│   └── nginx.conf
│
├── docs/                     # Documentation
│   └── solid-refactoring/    # SOLID refactoring docs
│       ├── 01-ANALYSIS.md
│       ├── 02-IMPLEMENTATION-PLAN.md
│       ├── 03-IMPLEMENTATION-SUMMARY.md
│       └── 04-PHASE4-TESTING-SUMMARY.md
│
├── .github/                  # GitHub Actions
│   └── workflows/
│       └── ci-cd.yml         # CI/CD pipeline
│
├── ARCHITECTURE.md           # Architecture documentation
├── README.md                 # This file
├── docker-compose.yml        # Docker Compose config
└── Makefile                  # Make commands
```

---

## Development

### Service Layer Architecture

The application follows **SOLID principles** with a clean service layer:

#### Node.js Services

**HttpClient** (`services/httpClient.js`)
- Abstracts HTTP communication with Python API
- Handles request/response interceptors
- Normalizes error responses

**FileService** (`services/fileService.js`)
- Manages file uploads and validation
- Configures Multer middleware
- Handles file cleanup

**ResumeService** (`services/resumeService.js`)
- Orchestrates resume screening workflow
- Validates input data
- Coordinates HttpClient and FileService

#### Python Services

**SimilarityService** (`services/similarityService.py`)
- Abstract base class for similarity calculators
- BERT implementation for production
- Mock implementation for testing

**Scoring Service** (`utils/scoring.py`)
- Configuration-driven scoring
- Multi-factor evaluation (skills, experience, education, general)
- Explainable AI - generates human-readable explanations

### Adding New Features

1. **Configuration First**: Add config to appropriate config file
2. **Create Service**: Implement business logic in service layer
3. **Write Tests**: Achieve 80%+ coverage for new code
4. **Update Documentation**: Update ARCHITECTURE.md if needed
5. **Integration**: Wire up service in app.js/app.py

### Code Style

- **Node.js**: Follow existing patterns, use ES6+
- **Python**: PEP 8 compliance, type hints where appropriate
- **Tests**: Descriptive test names, arrange-act-assert pattern

---

## Documentation

### Available Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive architecture guide
  - System overview and component architecture
  - SOLID principles implementation
  - Service layer design patterns
  - Configuration management
  - Data flow diagrams
  - Testing strategy
  - Deployment architecture

- **[docs/solid-refactoring/](docs/solid-refactoring/)** - SOLID refactoring documentation
  - **01-ANALYSIS.md** - Initial code analysis and issues identified
  - **02-IMPLEMENTATION-PLAN.md** - 4-phase implementation plan
  - **03-IMPLEMENTATION-SUMMARY.md** - Phases 1-3 implementation details
  - **04-PHASE4-TESTING-SUMMARY.md** - Testing and documentation summary

### API Documentation

#### Resume Screening Endpoint

**POST** `/resume-screening`

**Request** (multipart/form-data):
```javascript
{
  jobDescription: string,  // Job description text
  skills: string,          // Comma-separated skills
  education: string,       // Required education level
  experience: string,      // "X years"
  resumes: File[]         // PDF files (max 10, 10MB each)
}
```

**Response**:
```javascript
[
  {
    filename: string,
    ts: number,            // Total score (0-100)
    ss: number,            // Skills score
    ex: number,            // Experience score
    ed: number,            // Education score
    ge: number,            // General score
    explanation: string,   // Human-readable explanation
    resume_text: string,
    r_skills: string,
    education: string,
    experience: number
  }
]
```

---

## Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Write tests** to achieve 80%+ coverage
5. **Run tests** (`npm test` and `pytest`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Pull Request Guidelines

- Follow existing code style and patterns
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Keep PRs focused on a single feature/fix

### Code Review Process

1. Automated tests must pass (GitHub Actions)
2. Code coverage must meet 80% threshold
3. At least one maintainer approval required
4. Security scan must pass (Trivy, npm audit)

---

## Performance Metrics

### Test Execution

- **Node.js Tests**: ~0.4 seconds (72 tests)
- **Python Tests**: ~2 minutes (parallel execution)
- **Total CI/CD Pipeline**: ~8 minutes

### Coverage

- **Overall Coverage**: 87.65%
- **Statements**: 87.65%
- **Branches**: 92.95%
- **Functions**: 82.92%
- **Lines**: 87.26%

### Optimizations

- BERT model session caching (50% test speedup)
- Parallel test execution (pytest-xdist)
- Git history cleanup (95% push time reduction)
- Docker layer caching

---

## Troubleshooting

### Common Issues

**Issue**: Python API not connecting
```bash
# Check if Python API is running
curl http://localhost:5000/health

# Check Docker logs
docker-compose logs python-api
```

**Issue**: BERT model download fails
```bash
# Set proxy if behind firewall
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# Or use local model cache
export LOCAL_FILES_ONLY=true
```

**Issue**: File upload fails
```bash
# Check upload directory exists and is writable
mkdir -p uploads
chmod 755 uploads
```

**Issue**: Tests failing
```bash
# Clear Jest cache
npx jest --clearCache

# Clear pytest cache
pytest --cache-clear
```

---

## License

GPL-2.0 or later

---

## Author

**Anne Ezurike**

---

## Acknowledgments

- BERT model: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- Sentence Transformers library
- Open source community

---

## Project Status

**Version**: 2.0.0
**Status**: Production Ready
**Last Updated**: October 2025

### Recent Updates

- ✅ SOLID refactoring complete (Phases 1-4)
- ✅ 87.65% test coverage achieved
- ✅ Comprehensive architecture documentation
- ✅ CI/CD pipeline optimized (60% faster)
- ✅ Parallel test execution implemented

### Roadmap

- [ ] Add support for DOCX/DOC files
- [ ] Implement user authentication
- [ ] Add historical analytics dashboard
- [ ] Kubernetes deployment configuration
- [ ] Multi-language resume support

---

For detailed technical information, see [ARCHITECTURE.md](ARCHITECTURE.md)
