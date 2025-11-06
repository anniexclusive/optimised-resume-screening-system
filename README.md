# AI Resume Screening System

AI-powered resume screening using BERT-based natural language processing to automate resume evaluation.

## Features

- **AI-Powered Screening**: BERT semantic similarity for matching resumes to job requirements
- **Multi-Factor Scoring**: Skills (40%), Experience (30%), Education (20%), General Match (10%)
- **Batch Processing**: Upload and screen multiple resumes simultaneously
- **PDF Support**: Automatic text extraction from PDF resumes
- **Docker Ready**: Full containerization with Docker Compose

## Architecture

Simple 3-tier architecture:

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
│     (nginx)     │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼────┐  ┌─▼─────────┐
│Node.js │──│  Python   │
│Backend │  │ AI Service│
│ 3001   │  │   5000    │
└────────┘  └───────────┘
```

### Components

- **Frontend**: React app served via nginx
- **Backend**: Express.js API handling file uploads and orchestration
- **AI Service**: Flask API with BERT model for semantic matching

## Technology Stack

**Frontend**
- React 19.0
- Axios for HTTP requests

**Backend**
- Express 4.21
- Multer for file uploads
- Axios for Python API calls

**AI Service**
- Flask 3.1
- Sentence Transformers 3.3 (BERT)
- PyTorch 2.6
- pypdf 5.1 for PDF processing

**DevOps**
- Docker & Docker Compose
- GitHub Actions CI/CD

## Prerequisites

- Docker & Docker Compose (recommended)
- OR Node.js 18+ and Python 3.9+ (for local development)

## Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/ai-resume-screening.git
cd ai-resume-screening

# Start all services
make up

# View logs
make logs

# Stop services
make down
```

Access the application at http://localhost:3000

### Local Development

**Terminal 1: Python API**
```bash
cd python-api
pip install -r requirements.txt
python app.py
# Running on http://localhost:5000
```

**Terminal 2: Node.js Backend**
```bash
cd node-resume
npm install
npm start
# Running on http://localhost:3001
```

**Terminal 3: React Frontend**
```bash
cd node-resume/client
npm install
npm start
# Running on http://localhost:3000
```

## Configuration

### Backend Environment Variables

Create `node-resume/.env`:

```bash
NODE_ENV=development
PORT=3001
PYTHON_API_URL=http://localhost:5000
CORS_ORIGIN=http://localhost:3000
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES=10
```

### Python API Environment Variables

Create `python-api/.env`:

```bash
FLASK_PORT=5000
FLASK_DEBUG=false
BERT_MODEL=all-MiniLM-L6-v2
DEVICE=cpu

# Scoring weights (must sum to 1.0)
WEIGHT_GENERAL=0.10
WEIGHT_SKILLS=0.40
WEIGHT_EXPERIENCE=0.30
WEIGHT_EDUCATION=0.20
```

## Testing

```bash
# Run all tests
make test

# Or run individually
cd node-resume && npm test
cd python-api && pytest
```

## Available Commands

```bash
make up       # Start all services
make down     # Stop all services
make build    # Build Docker images
make logs     # View logs
make test     # Run tests
make clean    # Clean temp files
```

## Project Structure

```
ai-resume-screening/
├── node-resume/              # Node.js Backend
│   ├── config/               # Configuration
│   ├── services/             # Business logic
│   │   ├── fileService.js    # File handling
│   │   └── resumeService.js  # Resume processing
│   ├── tests/                # Unit tests
│   ├── app.js                # Express app
│   └── client/               # React Frontend
│       ├── src/
│       └── public/
│
├── python-api/               # Python AI Service
│   ├── config/               # Configuration
│   ├── services/             # BERT similarity
│   ├── utils/                # Scoring & extraction
│   ├── tests/                # Unit tests
│   └── app.py                # Flask app
│
├── docker-compose.yml        # Docker services
├── Makefile                  # Commands
└── README.md                 # This file
```

## API Usage

### Resume Screening Endpoint

**POST** `/upload`

**Request** (multipart/form-data):
```javascript
{
  jobDescription: string,    // Job description
  skills: string,            // Comma-separated skills
  education: string,         // Education requirements
  experience: string,        // Experience requirements
  resumes: File[]           // PDF files (max 10)
}
```

**Response**:
```javascript
{
  "success": true,
  "total_processed": 2,
  "results": [
    {
      "filename": "resume.pdf",
      "ts": 85.5,              // Total score
      "ss": 35.0,              // Skills score
      "ex": 28.5,              // Experience score
      "ed": 18.0,              // Education score
      "ge": 4.0,               // General match score
      "explanation": "Strong match..."
    }
  ]
}
```

## Troubleshooting

**Services not starting?**
```bash
docker-compose down
docker-compose up -d --build
```

**Python API connection issues?**
```bash
# Check health
curl http://localhost:5000/health

# Check logs
docker logs resume-python-api
```

**File upload fails?**
```bash
# Ensure upload directory exists
mkdir -p node-resume/uploads
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

GPL-2.0 or later

## Author

Anne Ezurike

---

**Status**: Production Ready
**Last Updated**: November 2025
