# 🔄 CI/CD Pipeline for Resume Screening System

## 📖 Overview

This repository includes a production-ready CI/CD pipeline that automates testing, building, security scanning, and deployment of the Resume Screening System across multiple environments.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Backend    │  │   Frontend   │  │  Python API  │      │
│  │  (Node.js)   │  │   (React)    │  │   (BERT)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 1: Test & Build                               │   │
│  │  • Lint code (ESLint, Flake8)                        │   │
│  │  • Run unit tests (Jest, Pytest)                     │   │
│  │  • Build artifacts                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 2: Security Scan                              │   │
│  │  • Trivy vulnerability scan                          │   │
│  │  • npm/pip audit                                      │   │
│  │  • SAST analysis                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 3: Docker Build & Push                        │   │
│  │  • Build multi-stage images                          │   │
│  │  • Push to Docker Hub                                │   │
│  │  • Tag with version/branch                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 4: Deploy                                     │   │
│  │  • Staging (develop branch)                          │   │
│  │  • Production (main branch)                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Deployment Environments                         │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │     Staging      │         │    Production    │         │
│  │  (Auto-deploy)   │         │  (Auto-deploy)   │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### ✅ Automated Testing
- **Backend**: ESLint + Jest
- **Frontend**: ESLint + Jest + React Testing Library
- **Python API**: Flake8 + Pylint + Pytest
- Code coverage reporting to Codecov

### 🔒 Security
- Trivy vulnerability scanning
- npm/pip security audits
- SARIF reports to GitHub Security
- Dependency vulnerability alerts

### 🐳 Containerization
- Multi-stage Docker builds for optimized images
- Separate Dockerfiles for each service
- Docker Compose for local development
- Kubernetes manifests for production

### 📊 Monitoring & Observability
- Prometheus metrics collection
- Grafana dashboards
- Loki log aggregation
- Jaeger distributed tracing
- AlertManager for notifications

### 🔄 Deployment Strategies
- **Staging**: Auto-deploy on push to `develop`
- **Production**: Auto-deploy on push to `main`
- **Blue-Green**: Kubernetes rolling updates
- **Rollback**: Git revert + redeploy

## 📁 File Structure

```
optimised-resume-screening-system/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml              # Main CI/CD pipeline
│       ├── release.yml            # Release automation
│       └── PULL_REQUEST_TEMPLATE.md
├── node-resume/                   # Backend service
│   ├── Dockerfile
│   ├── package.json
│   └── app.js
├── node-resume/client/            # Frontend service
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
├── python-api/                    # ML API service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── predictbert.py
├── k8s/                          # Kubernetes configs
│   └── deployment.yaml
├── nginx/                        # Reverse proxy
│   └── nginx.conf
├── monitoring/                   # Monitoring stack
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── alertmanager/
├── docker-compose.yml
├── docker-compose.monitoring.yml
├── Makefile
├── .env.example
├── .gitignore
├── .dockerignore
├── scripts/
│   └── setup-cicd.sh
├── QUICKSTART.md
├── CI-CD-DOCUMENTATION.md
├── DEPLOYMENT-CHECKLIST.md
└── README-CICD.md (this file)
```

## 🔧 Setup Instructions

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/anniexclusive/optimised-resume-screening-system.git
cd optimised-resume-screening-system

# Run setup script
make setup

# Or run directly:
# chmod +x scripts/setup-cicd.sh
# ./scripts/setup-cicd.sh

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings
```

### 2. Configure GitHub Secrets

Navigate to: `Settings → Secrets and Variables → Actions → New repository secret`

Add the following secrets:

| Secret | Description | Example |
|--------|-------------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `youruser` |
| `DOCKER_PASSWORD` | Docker Hub token | `dckr_pat_xxxxx` |
| `STAGING_HOST` | Staging server | `staging.example.com` |
| `STAGING_USERNAME` | SSH user | `deploy` |
| `STAGING_SSH_KEY` | SSH private key | `-----BEGIN OPENSSH...` |
| `PRODUCTION_HOST` | Production server | `app.example.com` |
| `PRODUCTION_USERNAME` | SSH user | `deploy` |
| `PRODUCTION_SSH_KEY` | SSH private key | `-----BEGIN OPENSSH...` |
| `SLACK_WEBHOOK` | Slack webhook (optional) | `https://hooks.slack.com/...` |

### 3. Configure Branch Protection

Navigate to: `Settings → Branches → Add rule`

For `main` and `develop` branches:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators

### 4. Test the Pipeline

```bash
# Create a test branch
git checkout -b test/cicd-pipeline

# Make a small change
echo "# CI/CD Test" >> TEST.md

# Commit and push
git add TEST.md
git commit -m "test: CI/CD pipeline"
git push origin test/cicd-pipeline

# Watch the pipeline run in GitHub Actions
```

## 🎯 Usage

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test locally
make test
make lint

# 3. Commit changes
git add .
git commit -m "feat: add new feature"

# 4. Push and create PR
git push origin feature/new-feature
# Create PR on GitHub

# 5. After PR approval and merge to develop
# Pipeline automatically deploys to staging
```

### Release Process

```bash
# 1. Ensure develop is stable and tested
git checkout develop
git pull origin develop

# 2. Merge to main
git checkout main
git merge develop

# 3. Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"

# 4. Push to trigger production deployment
git push origin main
git push origin v1.0.0
```

### Manual Deployment

```bash
# Deploy to staging
git push origin develop

# Deploy to production
git push origin main

# Deploy specific version
git tag v1.0.1
git push origin v1.0.1
```

## 📊 Monitoring

### Access Monitoring Dashboards

```bash
# Start monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access dashboards
open http://localhost:3003   # Grafana (admin/admin)
open http://localhost:9090   # Prometheus
open http://localhost:16686  # Jaeger
```

### Key Metrics to Monitor

- **Request Rate**: Requests per second
- **Error Rate**: Percentage of 5xx responses
- **Response Time**: P50, P95, P99 latencies
- **CPU Usage**: Per container and host
- **Memory Usage**: Per container and host
- **Disk Usage**: Available disk space

### Alerts

Alerts are configured in `monitoring/prometheus/alerts.yml`:
- Service down (2 min)
- High CPU usage (>80% for 5 min)
- High memory usage (>85% for 5 min)
- Disk space low (<15%)
- High API latency (>2s)
- High error rate (>5%)

## 🐛 Troubleshooting

### Pipeline Fails at Test Stage

```bash
# Run tests locally
make test

# Check test coverage
npm test -- --coverage  # Frontend/Backend
pytest --cov  # Python API
```

### Docker Build Fails

```bash
# Build locally to see errors
docker build -t test-image -f node-resume/Dockerfile node-resume/

# Check Docker logs
docker logs <container-id>
```

### Deployment Fails

```bash
# SSH to server and check logs
ssh deploy@production-host
cd /opt/resume-screening
docker-compose logs -f

# Check container status
docker-compose ps
```

### High Memory Usage

```bash
# Check container memory
docker stats

# Restart specific service
docker-compose restart python-api
```

## 🔐 Security Best Practices

1. **Secrets Management**
   - Never commit secrets to Git
   - Use GitHub Secrets for CI/CD
   - Rotate secrets regularly (quarterly)
   - Use different secrets for staging/production

2. **Access Control**
   - Limit SSH access to specific IPs
   - Use SSH keys, not passwords
   - Enable 2FA on GitHub and Docker Hub
   - Review access logs regularly

3. **Dependency Management**
   - Run `npm audit` and `pip check` regularly
   - Update dependencies monthly
   - Review security advisories
   - Use Dependabot for automated updates

4. **Container Security**
   - Use official base images
   - Run containers as non-root users
   - Scan images with Trivy
   - Keep images updated

## 📈 Performance Optimization

### Frontend
- Enable code splitting
- Implement lazy loading
- Optimize bundle size
- Use CDN for static assets
- Enable service workers

### Backend
- Implement caching (Redis)
- Use connection pooling
- Enable compression
- Optimize database queries
- Implement rate limiting

### Python API
- Use model quantization
- Implement request batching
- Cache predictions
- Use async processing
- Optimize model loading

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/anniexclusive/optimised-resume-screening-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/anniexclusive/optimised-resume-screening-system/discussions)
- **Email**: [Contact Maintainer](mailto:anne@example.com)

## 📚 Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [CI-CD-DOCUMENTATION.md](CI-CD-DOCUMENTATION.md) - Detailed pipeline documentation
- [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md) - Pre-deployment checklist

## 📄 License

GPL-2.0 or later

## 👥 Contributors

- **Anne Ezurike** - Original Author - [@anniexclusive](https://github.com/anniexclusive)

## 🙏 Acknowledgments

- Anthropic Claude for CI/CD assistance
- Open source community for tools and inspiration

---

**Built with ❤️ for automated, reliable deployments**