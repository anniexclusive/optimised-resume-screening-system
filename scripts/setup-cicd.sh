#!/bin/bash

# CI/CD Setup Script for Resume Screening System
# Author: Generated for anniexclusive/optimised-resume-screening-system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing=0
    
    if ! command -v git &> /dev/null; then
        print_error "git is not installed"
        missing=$((missing + 1))
    else
        print_success "git is installed"
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        missing=$((missing + 1))
    else
        print_success "Node.js $(node --version) is installed"
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        missing=$((missing + 1))
    else
        print_success "npm $(npm --version) is installed"
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        missing=$((missing + 1))
    else
        print_success "Python $(python3 --version) is installed"
    fi
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed (optional for local development)"
    else
        print_success "Docker $(docker --version) is installed"
    fi
    
    if [ $missing -gt 0 ]; then
        print_error "Please install missing prerequisites and run again"
        exit 1
    fi
    
    echo ""
}

# Create directory structure
create_directories() {
    print_header "Creating Directory Structure"
    
    mkdir -p .github/workflows
    mkdir -p nginx
    mkdir -p k8s
    mkdir -p logs
    mkdir -p uploads
    
    print_success "Directories created"
    echo ""
}

# Create GitHub Actions workflows
create_workflows() {
    print_header "Creating GitHub Actions Workflows"
    
    # Note: The actual workflow content should be copied from the artifacts
    
    if [ ! -f .github/workflows/ci-cd.yml ]; then
        print_warning "Please copy ci-cd.yml to .github/workflows/"
    else
        print_success "ci-cd.yml exists"
    fi
    
    if [ ! -f .github/workflows/release.yml ]; then
        print_warning "Please copy release.yml to .github/workflows/"
    else
        print_success "release.yml exists"
    fi
    
    echo ""
}

# Create Dockerfiles
create_dockerfiles() {
    print_header "Creating Dockerfiles"
    
    # Check if Dockerfiles exist in appropriate directories
    local dockerfiles=(
        "node-resume/Dockerfile"
        "node-resume/client/Dockerfile"
        "python-api/Dockerfile"
    )
    
    for dockerfile in "${dockerfiles[@]}"; do
        if [ ! -f "$dockerfile" ]; then
            print_warning "Please create $dockerfile"
        else
            print_success "$dockerfile exists"
        fi
    done
    
    echo ""
}

# Setup environment file
setup_environment() {
    print_header "Setting Up Environment"
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env from .env.example"
            print_warning "Please edit .env with your configuration"
        else
            print_warning "Please create .env file"
        fi
    else
        print_success ".env file exists"
    fi
    
    echo ""
}

# Initialize Git hooks
setup_git_hooks() {
    print_header "Setting Up Git Hooks"
    
    if [ -d .git ]; then
        # Pre-commit hook for linting
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "Running pre-commit checks..."

# Run linting
make lint

if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix errors before committing."
    exit 1
fi

echo "Pre-commit checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        print_success "Git hooks configured"
    else
        print_warning "Not a git repository. Skipping git hooks."
    fi
    
    echo ""
}

# Create health check endpoints
create_health_endpoints() {
    print_header "Creating Health Check Endpoints"
    
    # Backend health endpoint
    if [ -f node-resume/app.js ]; then
        if ! grep -q "/health" node-resume/app.js; then
            print_warning "Add health check endpoint to node-resume/app.js:"
            echo "  app.get('/health', (req, res) => res.json({ status: 'ok' }));"
        else
            print_success "Backend health endpoint exists"
        fi
    fi
    
    # Python API health endpoint
    if [ -f python-api/predictbert.py ]; then
        if ! grep -q "/health" python-api/predictbert.py; then
            print_warning "Add health check endpoint to python-api/predictbert.py:"
            echo "  @app.route('/health')"
            echo "  def health(): return jsonify({'status': 'ok'})"
        else
            print_success "Python API health endpoint exists"
        fi
    fi
    
    echo ""
}

# Setup testing framework
setup_tests() {
    print_header "Setting Up Testing Framework"
    
    # Backend tests
    if [ -d node-resume ]; then
        cd node-resume
        if [ ! -d "__tests__" ] && [ ! -d "test" ]; then
            mkdir -p __tests__
            print_warning "Created __tests__ directory. Please add tests."
        else
            print_success "Backend test directory exists"
        fi
        cd ..
    fi
    
    # Frontend tests
    if [ -d node-resume/client ]; then
        cd node-resume/client
        if [ ! -d "src/__tests__" ]; then
            mkdir -p src/__tests__
            print_warning "Created test directory. Please add tests."
        else
            print_success "Frontend test directory exists"
        fi
        cd ../..
    fi
    
    # Python tests
    if [ -d python-api ]; then
        cd python-api
        if [ ! -d "tests" ]; then
            mkdir -p tests
            touch tests/__init__.py
            print_warning "Created tests directory. Please add tests."
        else
            print_success "Python test directory exists"
        fi
        cd ..
    fi
    
    echo ""
}

# Generate documentation
generate_docs() {
    print_header "Generating Documentation"
    
    if [ ! -f CI-CD-DOCUMENTATION.md ]; then
        print_warning "Please create CI-CD-DOCUMENTATION.md"
    else
        print_success "Documentation exists"
    fi
    
    echo ""
}

# Final instructions
print_final_instructions() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}Next Steps:${NC}"
    echo ""
    echo "1. Configure GitHub Secrets:"
    echo "   - DOCKER_USERNAME and DOCKER_PASSWORD"
    echo "   - STAGING_HOST, STAGING_USERNAME, STAGING_SSH_KEY"
    echo "   - PRODUCTION_HOST, PRODUCTION_USERNAME, PRODUCTION_SSH_KEY"
    echo "   - SLACK_WEBHOOK (optional)"
    echo ""
    echo "2. Update .env file with your configuration"
    echo ""
    echo "3. Copy all artifact files to appropriate locations:"
    echo "   - .github/workflows/ci-cd.yml"
    echo "   - .github/workflows/release.yml"
    echo "   - Dockerfiles to respective directories"
    echo "   - docker-compose.yml to root"
    echo "   - k8s/ configuration files"
    echo ""
    echo "4. Add health check endpoints to your applications"
    echo ""
    echo "5. Write tests for your components"
    echo ""
    echo "6. Commit and push to trigger CI/CD:"
    echo "   git add ."
    echo "   git commit -m 'Add CI/CD pipeline'"
    echo "   git push origin develop"
    echo ""
    echo -e "${CYAN}For detailed information, see CI-CD-DOCUMENTATION.md${NC}"
    echo ""
}

# Main execution
main() {
    echo ""
    print_header "Resume Screening System - CI/CD Setup"
    echo ""
    
    check_prerequisites
    create_directories
    create_workflows
    create_dockerfiles
    setup_environment
    setup_git_hooks
    create_health_endpoints
    setup_tests
    generate_docs
    print_final_instructions
}

# Run main function
main