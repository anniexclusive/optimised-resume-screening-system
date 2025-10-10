# 🚀 CI/CD Implementation Guide

## Complete Step-by-Step Implementation for Resume Screening System

This guide will walk you through implementing the entire CI/CD pipeline from scratch.

---

## 📋 Phase 1: Preparation (15 minutes)

### Step 1: Gather Required Information

Before starting, collect the following:

- [ ] **Docker Hub Account**: Username and access token
- [ ] **Server Details**: IP addresses or hostnames for staging/production
- [ ] **SSH Keys**: Private keys for server access
- [ ] **Domain Names**: URLs for your environments
- [ ] **Slack Webhook**: (Optional) For notifications

### Step 2: Install Prerequisites

```bash
# macOS
brew install git node python docker docker-compose

# Ubuntu/Debian
sudo apt update
sudo apt install -y git nodejs npm python3 python3-pip docker.io docker-compose

# Verify installations
git --version
node --version
python3 --version
docker --version
docker-compose --version
```

---

## 📦 Phase 2: Repository Setup (20 minutes)

### Step 1: Clone and Navigate

```bash
cd ~/projects  # or your preferred location
git clone https://github.com/anniexclusive/optimised-resume-screening-system.git
cd optimised-resume-screening-system
```

### Step 2: Create Directory Structure

```bash
# Create all necessary directories
mkdir -p .github/workflows
mkdir -p nginx
mkdir -p k8s
mkdir -p monitoring/{prometheus,grafana,loki,promtail,alertmanager}
mkdir -p logs
mkdir -p uploads
mkdir -p models

# Create placeholder files
touch uploads/.gitkeep
touch models/.gitkeep
```

### Step 3: Copy CI/CD Files

Create the following files in your repository. Copy content from the artifacts provided:

```bash
# GitHub Actions Workflows
touch .github/workflows/ci-cd.yml
touch .github/workflows/release.yml
touch .github/PULL_REQUEST_TEMPLATE.md

# Docker files
touch Dockerfile
touch node-resume/Dockerfile
touch node-resume/client/Dockerfile
touch node-resume/client/nginx.conf
touch python-api/Dockerfile

# Orchestration
touch docker-compose.yml
touch docker-compose.monitoring.yml

# Nginx configuration
touch nginx/nginx.conf

# Kubernetes
touch k8s/deployment.yaml

# Monitoring
touch monitoring/prometheus/prometheus.yml
touch monitoring/prometheus/alerts.yml

# Configuration
touch .env.example
touch .gitignore
touch .dockerignore
touch Makefile
mkdir -p scripts
touch scripts/setup-cicd.sh

# Documentation
touch QUICKSTART.md
touch CI-CD-DOCUMENTATION.md
touch DEPLOYMENT-CHECKLIST.md
touch README-CICD.md
touch IMPLEMENTATION-GUIDE.md
```

**Important**: Copy the actual content from each artifact into these files!

### Step 4: Make Scripts Executable

```bash
chmod +x scripts/setup-cicd.sh
chmod +x Makefile
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

Update these critical values in `.env`:
```bash
NODE_ENV=production
FLASK_ENV=production
REACT_APP_API_URL=https://your-domain.com/api
PYTHON_API_URL=http://python-api:5000
```

---

## 🔐 Phase 3: GitHub Configuration (15 minutes)

### Step 1: Create Docker Hub Token

1. Go to [Docker Hub](https://hub.docker.com)
2. Navigate to: **Account Settings → Security → New Access Token**
3. Name: `github-actions-resume-screening`
4. Copy the token (you won't see it again!)

### Step 2: Generate SSH Keys for Deployment

```bash
# Generate new SSH key pair for CI/CD
ssh-keygen -t ed25519 -f ~/.ssh/resume_cicd_deploy -C "cicd-deploy" -N ""

# Copy public key to servers
ssh-copy-id -i ~/.ssh/resume_cicd_deploy.pub deploy@staging-server
ssh-copy-id -i ~/.ssh/resume_cicd_deploy.pub deploy@production-server

# Get private key content for GitHub Secret
cat ~/.ssh/resume_cicd_deploy
# Copy the entire output including BEGIN and END lines
```

### Step 3: Configure GitHub Secrets

Navigate to your GitHub repository:
```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets one by one:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `DOCKER_USERNAME` | Your Docker Hub username | From Docker Hub account |
| `DOCKER_PASSWORD` | Docker Hub access token | From Step 1 above |
| `STAGING_HOST` | `staging.example.com` | Your staging server |
| `STAGING_USERNAME` | `deploy` | SSH username |
| `STAGING_SSH_KEY` | Private key content | From Step 2 above |
| `PRODUCTION_HOST` | `app.example.com` | Your production server |
| `PRODUCTION_USERNAME` | `deploy` | SSH username |
| `PRODUCTION_SSH_KEY` | Private key content | From Step 2 above |
| `SLACK_WEBHOOK` | `https://hooks.slack.com/...` | Optional: From Slack |

### Step 4: Configure Branch Protection

Navigate to: `Settings → Branches → Add branch protection rule`

**For `main` branch:**
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass before merging
  - Search and select: `backend-test`, `frontend-test`, `python-api-test`
- ✅ Require branches to be up to date before merging
- ✅ Include administrators

**For `develop` branch:**
- Same settings as above

---

## 🖥️ Phase 4: Server Setup (30 minutes)

### Step 1: Prepare Servers

Run these commands on **both** staging and production servers:

```bash
# SSH into server
ssh deploy@your-server

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply group changes
exit
ssh deploy@your-server

# Verify installations
docker --version
docker-compose --version

# Create application directory
sudo mkdir -p /opt/resume-screening
sudo chown $USER:$USER /opt/resume-screening
cd /opt/resume-screening

# Create docker-compose.yml
nano docker-compose.yml
```

Copy this minimal `docker-compose.yml` to your server:

```yaml
version: '3.8'

services:
  python-api:
    image: yourusername/resume-python-api:latest
    ports:
      - "5000:5000"
    restart: unless-stopped

  backend:
    image: yourusername/resume-backend:latest
    ports:
      - "3001:3001"
    environment:
      - PYTHON_API_URL=http://python-api:5000
    depends_on:
      - python-api
    restart: unless-stopped

  frontend:
    image: yourusername/resume-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Step 2: Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### Step 3: Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot

# Get SSL certificate (requires DNS to be pointed to server)
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

---

## 🧪 Phase 5: Testing the Pipeline (20 minutes)

### Step 1: Test Locally First

```bash
# Return to your local repository
cd ~/projects/optimised-resume-screening-system

# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Try Docker build locally
docker-compose build
```

### Step 2: Add Health Check Endpoints

Add health check endpoints to your applications:

**Backend** (`node-resume/app.js`):
```javascript
// Add this route
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'backend'
  });
});
```

**Python API** (`python-api/predictbert.py`):
```python
# Add this route
@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'python-api'
    })
```

### Step 3: Commit and Push

```bash
# Create develop branch if it doesn't exist
git checkout -b develop

# Stage all files
git add .

# Commit
git commit -m "ci: add complete CI/CD pipeline

- Add GitHub Actions workflows for CI/CD
- Add Docker configurations for all services
- Add Kubernetes manifests
- Add monitoring stack with Prometheus and Grafana
- Add comprehensive documentation
- Add Makefile for development commands
- Configure health check endpoints"

# Push to GitHub
git push origin develop
```

### Step 4: Watch the Pipeline Run

1. Go to your GitHub repository
2. Click on **Actions** tab
3. You should see the workflow running
4. Monitor each step:
   - ✅ Backend tests
   - ✅ Frontend tests
   - ✅ Python API tests
   - ✅ Security scanning
   - ✅ Docker build and push
   - ✅ Deploy to staging (if on develop branch)

### Step 5: Verify Deployment

```bash
# Check staging deployment
curl http://staging.example.com/health

# SSH to staging server and check containers
ssh deploy@staging-server
cd /opt/resume-screening
docker-compose ps
docker-compose logs -f
```

---

## 🎯 Phase 6: Production Deployment (10 minutes)

### Step 1: Merge to Main

```bash
# Create pull request from develop to main
git checkout main
git pull origin main
git merge develop

# Push to trigger production deployment
git push origin main
```

### Step 2: Monitor Production Deployment

1. Watch GitHub Actions for production deployment
2. Approve deployment if manual approval is required
3. Wait for deployment to complete

### Step 3: Verify Production

```bash
# Test production endpoints
curl https://your-domain.com/health
curl https://your-domain.com/api/health

# Test frontend
open https://your-domain.com

# SSH to production and check
ssh deploy@production-server
cd /opt/resume-screening
docker-compose ps
```

---

## 📊 Phase 7: Setup Monitoring (15 minutes)

### Step 1: Deploy Monitoring Stack

```bash
# On your monitoring server (can be same as app server)
ssh deploy@monitoring-server

# Copy monitoring docker-compose
scp docker-compose.monitoring.yml deploy@monitoring-server:/opt/resume-screening/

# Start monitoring services
cd /opt/resume-screening
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Step 2: Configure Grafana

1. Access Grafana: `http://monitoring-server:3003`
2. Login: `admin` / `admin`
3. Change password when prompted
4. Add Prometheus data source:
   - URL: `http://prometheus:9090`
5. Import dashboards:
   - Dashboard ID `1860` (Node Exporter)
   - Dashboard ID `893` (Docker)
   - Dashboard ID `3662` (Prometheus 2.0 Stats)

### Step 3: Configure Alerts

```bash
# Edit alert configuration
nano /opt/resume-screening/monitoring/alertmanager/alertmanager.yml
```

Add your notification channels (Slack example):

```yaml
route:
  group_by: ['alertname']
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Resume Screening Alert'
```

---

## ✅ Phase 8: Validation (10 minutes)

### Complete This Checklist:

- [ ] All GitHub Actions workflows pass
- [ ] Docker images published to Docker Hub
- [ ] Staging environment accessible
- [ ] Production environment accessible
- [ ] Health checks return 200 OK
- [ ] Monitoring dashboards showing data
- [ ] Alerts configured and tested
- [ ] SSL certificates installed and valid
- [ ] Documentation reviewed and updated

### Test Critical Flows:

```bash
# Test resume upload (adjust command for your API)
curl -X POST -F "resume=@test-resume.pdf" \
  https://your-domain.com/api/upload

# Test screening (adjust for your API)
curl https://your-domain.com/api/screen/12345

# Check metrics
curl http://monitoring-server:9090/metrics
```

---

## 🎉 Success! What's Next?

### Immediate Next Steps:
1. ✅ Review logs for any warnings or errors
2. ✅ Test all user flows in production
3. ✅ Configure backup procedures
4. ✅ Document any custom configurations
5. ✅ Train team on deployment process

### Ongoing Maintenance:
- **Daily**: Check monitoring dashboards
- **Weekly**: Review error logs and metrics
- **Monthly**: Update dependencies
- **Quarterly**: Security audit and penetration testing

---

## 🆘 Troubleshooting Common Issues

### Issue: Pipeline Fails at Test Stage
```bash
# Run locally to debug
npm test
pytest -v
```

### Issue: Docker Image Won't Build
```bash
# Check Docker daemon
docker ps

# Build with verbose output
docker build --no-cache --progress=plain -f node-resume/Dockerfile .
```

### Issue: Can't SSH to Server
```bash
# Test SSH connection
ssh -v deploy@your-server

# Check SSH key permissions
chmod 600 ~/.ssh/resume_cicd_deploy
```

### Issue: Container Won't Start
```bash
# Check logs
docker logs <container-name>

# Check resource usage
docker stats
```

### Issue: High Memory Usage
```bash
# Restart services
docker-compose restart

# Check for memory leaks
docker stats --no-stream
```

---

## 📚 Additional Resources

- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **Docker Documentation**: https://docs.docker.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Prometheus Documentation**: https://prometheus.io/docs/

---

## 🎓 Training Your Team

Share these documents with your team:
1. `QUICKSTART.md` - For developers new to the project
2. `README-CICD.md` - For understanding the pipeline
3. `DEPLOYMENT-CHECKLIST.md` - For release managers
4. `CI-CD-DOCUMENTATION.md` - For detailed reference

---

## ✉️ Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Check server logs: `docker-compose logs -f`
4. Create an issue on GitHub
5. Contact the maintainer: @anniexclusive

---

**Congratulations! 🎊 Your CI/CD pipeline is now fully operational!**

The system will now automatically:
- ✅ Test every commit
- ✅ Build Docker images
- ✅ Scan for vulnerabilities
- ✅ Deploy to staging/production
- ✅ Monitor application health
- ✅ Alert on issues

Happy deploying! 🚀