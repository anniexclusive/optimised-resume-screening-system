# AI Resume Screening System - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Architecture](#component-architecture)
4. [Service Layer Design](#service-layer-design)
5. [Configuration Management](#configuration-management)
6. [Data Flow](#data-flow)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The AI Resume Screening System is a full-stack application that automates resume evaluation using BERT-based natural language processing. The system follows SOLID design principles and implements a microservices architecture.

### Technology Stack

**Frontend:**
- React 19.0
- React Router 6.30
- Modern JavaScript (ES6+)

**Backend (Node.js):**
- Express 4.21
- Axios for HTTP communication
- Multer for file uploads
- FormData for multipart requests

**AI Service (Python):**
- Flask 2.0
- Sentence Transformers (BERT)
- PyTorch 2.6
- PyPDF2 for PDF processing

**Infrastructure:**
- Docker & Docker Compose
- Nginx reverse proxy
- GitHub Actions CI/CD

---

## Architecture Principles

### SOLID Principles Implementation

#### 1. **Single Responsibility Principle (SRP)**
Each module has one well-defined responsibility:

- **ConfigurationService**: Manages all configuration
- **HttpClient**: Handles HTTP communications
- **FileService**: Manages file operations
- **ResumeService**: Orchestrates resume screening logic
- **SimilarityService**: Calculates semantic similarity

#### 2. **Open/Closed Principle (OCP)**
System is open for extension but closed for modification:

- Configuration can be extended via environment variables
- New similarity calculators can be added without modifying existing code
- Scoring weights are externalized to configuration

#### 3. **Liskov Substitution Principle (LSP)**
Abstractions can be replaced with implementations:

- `SimilarityCalculator` abstract base class
- `BERTSimilarityCalculator` and `MockSimilarityCalculator` implementations
- HttpClient can be swapped for testing

#### 4. **Interface Segregation Principle (ISP)**
Clients depend only on methods they use:

- Service interfaces are minimal and focused
- No fat interfaces with unused methods

#### 5. **Dependency Inversion Principle (DIP)**
High-level modules don't depend on low-level modules:

- Services depend on abstractions (HttpClient, FileService)
- Dependency injection used throughout
- Easy to mock for testing

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│              (React Frontend - Port 3000)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                      │
│                      (Port 80)                              │
└─────────────┬────────────────────────┬──────────────────────┘
              │                        │
              ▼                        ▼
┌─────────────────────────┐  ┌────────────────────────────────┐
│   Node.js Backend       │  │   Python AI Service            │
│   (Express - Port 3001) │──│   (Flask - Port 5000)          │
│                         │  │                                │
│  ┌──────────────────┐   │  │  ┌──────────────────────────┐  │
│  │  FileService     │   │  │  │  SimilarityService      │  │
│  └──────────────────┘   │  │  │  (BERT Model)           │  │
│  ┌──────────────────┐   │  │  └──────────────────────────┘  │
│  │  ResumeService   │   │  │  ┌──────────────────────────┐  │
│  └──────────────────┘   │  │  │  ScoringService         │  │
│  ┌──────────────────┐   │  │  └──────────────────────────┘  │
│  │  HttpClient      │   │  │  ┌──────────────────────────┐  │
│  └──────────────────┘   │  │  │  PDF Processing         │  │
│  ┌──────────────────┐   │  │  └──────────────────────────┘  │
│  │  Configuration   │   │  │                                │
│  └──────────────────┘   │  └────────────────────────────────┘
└─────────────────────────┘
```

---

## Service Layer Design

### Node.js Backend Services

#### 1. **HttpClient** (`services/httpClient.js`)

**Purpose**: Abstract HTTP communication with Python API

**Responsibilities:**
- Create and configure axios instances
- Handle request/response interceptors
- Normalize error responses
- Support various HTTP methods (GET, POST, PUT, DELETE)
- Handle FormData uploads

**Key Methods:**
```javascript
- get(url, config)
- post(url, data, config)
- put(url, data, config)
- delete(url, config)
- postFormData(url, formData)
- handleError(error)
```

**Configuration:**
- Base URL: `http://localhost:5000` (configurable)
- Timeout: 30000ms
- Headers: `Content-Type: application/json`

---

#### 2. **FileService** (`services/fileService.js`)

**Purpose**: Manage file uploads and validation

**Responsibilities:**
- Configure Multer storage
- Validate file types and sizes
- Create upload middleware
- Manage file cleanup
- Handle file streams

**Key Methods:**
```javascript
- ensureUploadDirectory()
- getMulterStorage()
- getUploadMiddleware()
- validateFile(file, callback)
- getFilePaths(files)
- createReadStreams(filePaths)
- deleteFile(filePath)
- deleteFiles(filePaths)
- cleanupOldFiles(maxAgeHours)
```

**Configuration:**
- Upload directory: `uploads/`
- Max file size: 10MB
- Allowed extensions: `.pdf`
- Max files: 10

---

#### 3. **ResumeService** (`services/resumeService.js`)

**Purpose**: Orchestrate resume screening workflow

**Responsibilities:**
- Validate screening input
- Prepare FormData for Python API
- Coordinate with HttpClient and FileService
- Handle errors and cleanup
- Parse and format data

**Key Methods:**
```javascript
- screenResumes(jobData, files)
- validateScreeningInput(jobData, files)
- prepareFormData(jobData, files)
- parseSkills(skillsString)
- handleError(error)
- cleanupFiles(files)
```

**Dependencies:**
- HttpClient (injected)
- FileService (injected)
- Configuration

---

### Python AI Service

#### 1. **SimilarityService** (`services/similarityService.py`)

**Purpose**: Calculate semantic similarity using BERT

**Architecture:**
```python
class SimilarityCalculator(ABC):
    """Abstract base class"""
    @abstractmethod
    def encode(self, text): pass

    @abstractmethod
    def compute_similarity(self, text1, text2): pass

class BERTSimilarityCalculator(SimilarityCalculator):
    """Production implementation using BERT"""
    model_name = 'all-MiniLM-L6-v2'

class MockSimilarityCalculator(SimilarityCalculator):
    """Fast mock for testing"""
```

**Singleton Pattern:**
- Single model instance shared across requests
- Reduces memory usage and load time
- Thread-safe implementation

---

#### 2. **Scoring Service** (`utils/scoring.py`)

**Purpose**: Calculate resume scores based on job requirements

**Scoring Components:**
1. **Skills Score (40%)**: Semantic similarity of skills
2. **Experience Score (30%)**: Years of experience match
3. **Education Score (20%)**: Education level alignment
4. **General Score (10%)**: Overall resume-job description match

**Key Functions:**
```python
- get_resume_ranking_score(ranking_data, job_data)
- compute_experience_score(resume_exp, job_exp, similarity)
- generate_explanation(scores)
- qualification_similarity(resume_qual, job_qual)
```

**Configuration-Driven:**
- Weights externalized to `scoring_config.py`
- Thresholds for "strong" candidates
- Experience scaling factors

---

## Configuration Management

### Centralized Configuration

All configuration is externalized following the **12-Factor App** methodology.

#### Node.js Configuration (`config/api.config.js`)

```javascript
module.exports = {
  env: process.env.NODE_ENV || 'development',

  server: {
    port: parseInt(process.env.PORT) || 3001,
    host: process.env.HOST || 'localhost'
  },

  pythonApi: {
    baseUrl: process.env.PYTHON_API_URL || 'http://localhost:5000',
    endpoints: {
      predictBert: '/predictbert',
      health: '/health'
    },
    timeout: parseInt(process.env.API_TIMEOUT) || 30000
  },

  upload: {
    directory: process.env.UPLOAD_DIR || 'uploads',
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024,
    allowedExtensions: ['.pdf'],
    maxFiles: parseInt(process.env.MAX_FILES) || 10
  },

  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true
  }
};
```

#### Python Configuration

**Model Config** (`config/model_config.py`):
```python
BERT_CONFIG = {
    'model_name': os.getenv('BERT_MODEL', 'all-MiniLM-L6-v2'),
    'cache_dir': os.getenv('MODEL_CACHE_DIR', './models'),
    'device': os.getenv('DEVICE', 'cpu'),
    'max_seq_length': int(os.getenv('MAX_SEQ_LENGTH', '256'))
}

MODEL_LOAD_CONFIG = {
    'lazy_loading': os.getenv('LAZY_LOAD', 'false').lower() == 'true',
    'show_progress': os.getenv('SHOW_PROGRESS', 'true').lower() == 'true',
    'local_files_only': os.getenv('LOCAL_FILES_ONLY', 'false').lower() == 'true'
}
```

**Scoring Config** (`config/scoring_config.py`):
```python
SCORING_WEIGHTS = {
    'general': float(os.getenv('WEIGHT_GENERAL', '0.10')),
    'skills': float(os.getenv('WEIGHT_SKILLS', '0.40')),
    'experience': float(os.getenv('WEIGHT_EXPERIENCE', '0.30')),
    'education': float(os.getenv('WEIGHT_EDUCATION', '0.20'))
}

THRESHOLDS = {
    'skills': {'strong': 30},
    'experience': {'strong': 20},
    'education': {'strong': 12},
    'general': {'strong': 7}
}
```

### Environment Variables

Create `.env` files for environment-specific configuration:

```bash
# Node.js Backend
NODE_ENV=production
PORT=3001
PYTHON_API_URL=http://python-api:5000
MAX_FILE_SIZE=10485760
MAX_FILES=10

# Python API
FLASK_PORT=5000
FLASK_DEBUG=false
BERT_MODEL=all-MiniLM-L6-v2
WEIGHT_SKILLS=0.40
WEIGHT_EXPERIENCE=0.30
WEIGHT_EDUCATION=0.20
WEIGHT_GENERAL=0.10
```

---

## Data Flow

### Resume Screening Workflow

```
┌────────────┐
│   User     │
│  (Browser) │
└─────┬──────┘
      │ 1. Upload Resume(s) + Job Requirements
      ▼
┌─────────────────┐
│  React Frontend │
│                 │
│  - Form         │
│  - Validation   │
│  - Upload UI    │
└────────┬────────┘
         │ 2. POST /resume-screening
         ▼
┌────────────────────────┐
│  Node.js Backend       │
│                        │
│  FileService           │
│  ├─ Validate files     │
│  ├─ Save to disk       │
│  └─ Generate paths     │
│                        │
│  ResumeService         │
│  ├─ Validate input     │
│  ├─ Prepare FormData   │
│  └─ Screen resumes     │
│                        │
│  HttpClient            │
│  └─ POST to Python API │
└───────────┬────────────┘
            │ 3. POST /predictbert
            ▼
┌────────────────────────────────┐
│     Python AI Service          │
│                                │
│  Flask Routes                  │
│  └─ /predictbert endpoint      │
│                                │
│  PDF Processing                │
│  ├─ Extract text from PDFs     │
│  ├─ Parse resume fields        │
│  └─ Clean and normalize        │
│                                │
│  SimilarityService             │
│  ├─ Load BERT model (cached)   │
│  ├─ Generate embeddings        │
│  └─ Compute cosine similarity  │
│                                │
│  Scoring Service               │
│  ├─ Skills score (40%)         │
│  ├─ Experience score (30%)     │
│  ├─ Education score (20%)      │
│  ├─ General score (10%)        │
│  └─ Generate explanation       │
└──────────────┬─────────────────┘
               │ 4. Return ranked results
               ▼
┌────────────────────────┐
│  Node.js Backend       │
│                        │
│  FileService           │
│  └─ Cleanup temp files │
└───────────┬────────────┘
            │ 5. Return JSON response
            ▼
┌─────────────────┐
│  React Frontend │
│                 │
│  - Display      │
│    results      │
│  - Show scores  │
│  - Rankings     │
└─────────────────┘
```

### Data Models

#### Job Requirements (Input)
```javascript
{
  jobDescription: string,  // Free-form text
  skills: string,          // Comma-separated
  education: string,       // Required education level
  experience: string       // "X years"
}
```

#### Resume Screening Result (Output)
```javascript
{
  filename: string,
  ts: number,              // Total score (0-100)
  ss: number,              // Skills score
  ex: number,              // Experience score
  ed: number,              // Education score
  ge: number,              // General score
  explanation: string,     // Human-readable explanation
  resume_text: string,     // Extracted text
  r_skills: string,        // Parsed skills
  education: string,       // Parsed education
  experience: number       // Parsed years
}
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │     E2E     │  ← Integration tests (manual)
        └─────────────┘
      ┌─────────────────┐
      │  Integration    │  ← API endpoint tests
      └─────────────────┘
    ┌───────────────────────┐
    │    Unit Tests         │  ← 80%+ coverage target
    └───────────────────────┘
```

### Unit Tests (Node.js)

**Framework**: Jest 29.7

**Coverage**: 87.65% (exceeds 80% target)

**Test Files:**
- `tests/httpClient.test.js` - 18 tests
- `tests/fileService.test.js` - 23 tests
- `tests/resumeService.test.js` - 31 tests

**Configuration** (`jest.config.js`):
```javascript
module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: ['services/**/*.js', 'config/**/*.js'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Unit Tests (Python)

**Framework**: pytest 7.4

**Parallel Execution**: pytest-xdist

**Test Files:**
- `tests/test_config.py` - Configuration tests
- `tests/test_scoring.py` - Scoring logic tests
- `tests/test_similarity_service.py` - BERT model tests
- `tests/test_api.py` - Flask endpoint tests

**Configuration** (`pytest.ini`):
```ini
[pytest]
addopts =
    -v
    --tb=short
    -n auto           # Parallel execution
    --timeout=30      # Test timeout
    --durations=10    # Show slowest tests
testpaths = tests
```

**Test Fixtures** (`conftest.py`):
- Session-scoped BERT model loading (faster tests)
- Mock similarity calculator for unit tests
- Sample job and resume data fixtures

### Integration Tests

**Location**: `tests/integration/`

**Purpose**: Test complete workflows

**Tests:**
- Resume screening end-to-end flow
- Multiple file uploads
- Error handling (invalid files, missing fields)
- Python API integration
- File cleanup

**Run Integration Tests:**
```bash
npm test -- tests/integration/
```

---

## Deployment Architecture

### Docker Compose Setup

The system uses Docker Compose for local development and deployment:

```yaml
services:
  frontend:
    build: ./node-resume/client
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:80

  backend:
    build: ./node-resume
    ports:
      - "3001:3001"
    environment:
      - PYTHON_API_URL=http://python-api:5000
    volumes:
      - ./uploads:/app/uploads

  python-api:
    build: ./python-api
    ports:
      - "5000:5000"
    environment:
      - FLASK_DEBUG=false
      - BERT_MODEL=all-MiniLM-L6-v2

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

### CI/CD Pipeline

**Platform**: GitHub Actions

**Workflow** (`.github/workflows/ci-cd.yml`):

1. **Backend Tests**
   - Install dependencies
   - Run linting
   - Run unit tests
   - Build backend

2. **Frontend Tests**
   - Install dependencies
   - Run linting
   - Run unit tests
   - Build production bundle

3. **Python API Tests**
   - Install dependencies
   - Run flake8 linting
   - Run pytest with coverage
   - Upload coverage reports

4. **Security Scanning**
   - Trivy vulnerability scanner
   - npm audit (backend & frontend)

5. **Docker Build & Push** (on push to main/develop)
   - Build Docker images
   - Tag with branch and SHA
   - Push to Docker Hub

**Performance Optimizations:**
- Parallel test execution (pytest-xdist)
- Docker layer caching
- Dependency caching (npm, pip)

---

## Performance Considerations

### BERT Model Optimization

1. **Model Selection**: `all-MiniLM-L6-v2` (80MB)
   - Faster than larger models
   - Good accuracy for resume screening
   - 384-dimensional embeddings

2. **Caching Strategy**:
   - Session-scoped model loading in tests
   - Singleton pattern in production
   - Model downloaded once, cached locally

3. **Inference Optimization**:
   - Batch processing for multiple resumes
   - CPU-optimized (torch 2.6.0)
   - MPS support for M1 Macs

### File Handling

1. **Upload Limits**:
   - Max file size: 10MB
   - Max files per request: 10
   - Allowed types: PDF only

2. **Cleanup Strategy**:
   - Automatic cleanup after processing
   - Old file cleanup (24-hour threshold)
   - Error-safe cleanup handling

### API Performance

1. **Timeout Configuration**:
   - Node.js → Python: 30 seconds
   - Frontend → Node.js: 30 seconds

2. **Error Handling**:
   - Graceful degradation
   - Retry logic for transient failures
   - Clear error messages

---

## Security Considerations

1. **File Upload Security**:
   - File type validation
   - Size limits enforced
   - Sanitized filenames
   - Temporary storage with cleanup

2. **API Security**:
   - CORS configuration
   - Request validation
   - Error message sanitization

3. **Dependency Security**:
   - Regular security audits (npm audit, pip)
   - Automated vulnerability scanning (Trivy)
   - Dependency pinning

---

## Future Enhancements

1. **Performance**:
   - Implement response caching
   - Add database for job/resume storage
   - Queue system for batch processing

2. **Features**:
   - Support for DOCX/DOC files
   - Multi-language support
   - Custom scoring weight configuration UI
   - Historical analytics dashboard

3. **Scalability**:
   - Kubernetes deployment
   - Horizontal scaling of Python API
   - Distributed model serving
   - Load balancing

4. **Monitoring**:
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry)
   - Metrics dashboard (Grafana)
   - Logging aggregation (ELK stack)

---

## Glossary

- **BERT**: Bidirectional Encoder Representations from Transformers
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Cosine Similarity**: Measure of similarity between two vectors
- **Embeddings**: Vector representations of text
- **FormData**: Multipart form data for file uploads
- **Multer**: Node.js middleware for handling multipart/form-data
- **Sentence Transformers**: Library for generating sentence embeddings

---

## Contact & Support

For questions or issues, please refer to:
- GitHub Issues: [Project Repository](https://github.com/your-repo/ai-resume-screening)
- Documentation: This file and `/docs` directory
- API Documentation: `/docs/API.md`

---

**Last Updated**: October 2025
**Version**: 2.0.0
**Maintainers**: Development Team
