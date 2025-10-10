# 🚀 Quick Start Guide

Get the Resume Screening System up and running in minutes!

## Prerequisites

- **Node.js** 18.x or higher
- **Python** 3.9 or higher
- **npm** or **yarn**
- **Docker** (optional, for containerized deployment)
- **Git**

## 🏃 Fast Track (5 minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/anniexclusive/optimised-resume-screening-system.git
cd optimised-resume-screening-system

# Run setup script
make setup
```

### 2. Install Dependencies

```bash
make install
```

Or manually:

```bash
# Backend
cd node-resume && npm install

# Frontend
cd node-resume/client && npm install

# Python API
cd python-api && pip install -r requirements.txt
```

### 3. Start the Application

**Option A: Using Make (Recommended)**
```bash
make start-all
```

**Option B: Using Docker Compose**
```bash
docker-compose up -d
```

**Option C: Manual Start**
```bash
# Terminal 1 - Python API
cd python-api
python predictbert.py

# Terminal 2 - Backend
cd node-resume
node app.js

# Terminal 3 - Frontend
cd node-resume/client
npm start
```

### 4. Access the Application

- 🌐 **Frontend**: http://localhost:3000
- ⚙️ **Backend API**: http://localhost:3001
- 🤖 **Python ML API**: http://localhost:5000

## 🐳 Docker Deployment

### Development
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Monitoring
```bash
# Start application with monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access monitoring dashboards
# Grafana: http://localhost:3003 (admin/admin)
# Prometheus: http://localhost:9090
# Jaeger: http://localhost:16686
```

## 🔧 Common Tasks

### Running Tests
```bash
make test
```

### Linting Code
```bash
make lint
```

### Building for Production
```bash
make build
```

### Cleaning Build Artifacts
```bash
make clean
```

### Health Check
```bash
make health-check
```

## 📝 Configuration

### Environment Variables

Edit `.env` file with your settings:

```bash
# Application
NODE_ENV=development
FLASK_ENV=development

# Ports
BACKEND_PORT=3001
FRONTEND_PORT=3000
PYTHON_API_PORT=5000

# API URLs
REACT_APP_API_URL=http://localhost:3001
PYTHON_API_URL=http://localhost:5000
```

### Adding Secrets

For CI/CD, add these secrets to GitHub:

1. Go to **Settings → Secrets and Variables → Actions**
2. Add the following secrets:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `STAGING_HOST`
   - `STAGING_SSH_KEY`
   - `PRODUCTION_HOST`
   - `PRODUCTION_SSH_KEY`

## 🔄 CI/CD Pipeline

### Triggering the Pipeline

**Push to develop (triggers staging deployment):**
```bash
git checkout develop
git add .
git commit -m "Your changes"
git push origin develop
```

**Push to main (triggers production deployment):**
```bash
git checkout main
git merge develop
git push origin main
```

**Creating a release:**
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🛠️ Troubleshooting

### Port Already in Use

```bash
# Find process using the port
lsof -i :3000  # or :3001, :5000

# Kill the process
kill -9 <PID>
```

### Docker Issues

```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Model Loading Errors

If BERT model fails to load:
```bash
# Ensure sufficient memory (at least 2GB available)
# Download model manually
cd python-api
python -c "from transformers import BertTokenizer, BertModel; BertTokenizer.from_pretrained('bert-base-uncased'); BertModel.from_pretrained('bert-base-uncased')"
```

## 📊 Monitoring

### Local Monitoring Setup

```bash
# Start with monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access dashboards
open http://localhost:3003  # Grafana
open http://localhost:9090  # Prometheus
open http://localhost:16686 # Jaeger
```

### Default Credentials

- **Grafana**: `admin` / `admin` (change on first login)

## 🎯 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

```bash
# Make your code changes
# Run tests locally
make test

# Run linting
make lint
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
# Go to GitHub and create Pull Request
```

### 5. After PR Approval

```bash
git checkout develop
git pull origin develop
git merge feature/your-feature-name
git push origin develop
```

## 🔐 Security Best Practices

1. **Never commit secrets** to Git
2. **Use environment variables** for sensitive data
3. **Rotate credentials** regularly
4. **Keep dependencies updated**: `npm audit fix`, `pip check`
5. **Review security scan results** in CI/CD

## 📚 Next Steps

1. Read the full [CI/CD Documentation](CI-CD-DOCUMENTATION.md)
2. Configure monitoring alerts in Prometheus
3. Set up Slack/email notifications
4. Review and customize Kubernetes configurations
5. Set up SSL certificates for production

## 🆘 Getting Help

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the `docs/` folder
- **CI/CD Logs**: View in GitHub Actions tab
- **Application Logs**: `make docker-logs` or check `logs/` folder

## 🔄 Update Guide

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
make install

# Rebuild Docker images
docker-compose build

# Restart services
docker-compose down && docker-compose up -d
```

### Updating CI/CD Pipeline

1. Edit workflow files in `.github/workflows/`
2. Test locally with [act](https://github.com/nektos/act)
3. Commit and push changes
4. Monitor GitHub Actions for execution

## 🎓 Learning Resources

### Docker & Containers
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### CI/CD
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CI/CD Best Practices](https://www.jenkins.io/doc/book/pipeline/best-practices/)

### Monitoring
- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Tutorials](https://grafana.com/tutorials/)

### Kubernetes
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Happy Coding! 🎉**

For detailed information, see [CI-CD-DOCUMENTATION.md](CI-CD-DOCUMENTATION.md)