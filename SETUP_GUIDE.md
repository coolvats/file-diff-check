# SETUP_GUIDE.md - Complete Setup Instructions

## Complete Step-by-Step Setup Guide

### Phase 1: Initial Setup

#### 1.1 Local Development Environment

```bash
# Clone repository
git clone https://github.com/your-username/file-check.git
cd file-check

# Create virtual environment (Python 3.11+)
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.2 Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Required:
# - LANGSMITH_API_KEY: Get from https://smith.langchain.com
# - SMTP_USERNAME: Your email address
# - SMTP_PASSWORD: App-specific password
# - APPROVAL_EMAIL: Approval recipient email
# - GITHUB_OWNER: Your GitHub username
# - GITHUB_REPO: Your repository name
```

#### 1.3 Verify Local Installation

```bash
# Run tests
pytest tests/ -v

# Start development server
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for API documentation
```

---

### Phase 2: GitHub Repository Setup

#### 2.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `file-check`
3. Initialize with README
4. Clone to local machine

#### 2.2 Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git remote add origin https://github.com/your-username/file-check.git

# Add and commit files
git add .
git commit -m "Initial commit: File duplicate checker API with CI/CD"

# Push to GitHub
git branch -M main
git push -u origin main
```

#### 2.3 Configure Branch Protection Rules

1. Go to **Settings → Branches**
2. Click **Add rule** under Branch protection rules
3. Set Pattern name: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews from code owners
5. Click **Create**

---

### Phase 3: GitHub Secrets Configuration

#### 3.1 Add Repository Secrets

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add each secret:

| Secret Name | Value | How to Get |
|---|---|---|
| `LANGSMITH_API_KEY` | Your LangSmith API key | https://smith.langchain.com → Settings → API keys |
| `SMTP_SERVER` | smtp.gmail.com | Email provider |
| `SMTP_PORT` | 587 | Email provider (usually 587 for TLS) |
| `SMTP_USERNAME` | your-email@gmail.com | Your email address |
| `SMTP_PASSWORD` | app-specific-password | Gmail: https://myaccount.google.com/apppasswords |
| `APPROVAL_EMAIL` | vatsalyamishra93@gmail.com | Approval recipient |
| `DEPLOYMENT_HOST` | your-server.com | Your production server |
| `DEPLOYMENT_USER` | deploy-user | SSH user for deployment |
| `DEPLOYMENT_KEY` | [SSH private key content] | Generate with `ssh-keygen` |

#### 3.2 Gmail App Password Setup (Important)

1. Enable 2-Factor Authentication: https://myaccount.google.com/security
2. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password
   - Use as `SMTP_PASSWORD` secret

---

### Phase 4: LangSmith Configuration

#### 4.1 Create LangSmith Account

1. Sign up at https://smith.langchain.com
2. Create project: "file-duplicate-checker"
3. Go to **Settings → API keys**
4. Create new API key
5. Copy API key to `LANGSMITH_API_KEY` secret

#### 4.2 Configure LangSmith Project

1. Go to project settings
2. Enable fleet management
3. Configure code review agent:
   - Name: "Code-Review-Agent"
   - Model: GPT-4 or Claude
   - Instructions: Focus on security and code quality

---

### Phase 5: GitHub Actions Verification

#### 5.1 Create Test PR

1. Create feature branch:
   ```bash
   git checkout -b test/setup-verification
   ```

2. Make minor change (e.g., update README):
   ```bash
   echo "# Test PR for verification" >> README.md
   git add .
   git commit -m "test: verify CI/CD pipeline"
   git push origin test/setup-verification
   ```

3. Create Pull Request on GitHub
4. Observe workflow execution

#### 5.2 Monitor Workflow Execution

1. Go to **Actions** tab
2. Select "PR Code Review and Approval" workflow
3. Watch jobs execute:
   - ✅ Security Scan
   - ✅ Dependency Scan
   - ✅ LangSmith Review
   - ✅ Tests
   - ✅ Approval Request

#### 5.3 Approve and Merge

1. Check email for approval request
2. Review approval link
3. Click to approve/reject
4. Merge PR (after approval)
5. Watch "Deploy to Production" workflow

---

### Phase 6: Production Deployment

#### 6.1 Server Setup

```bash
# On production server
mkdir -p /app
cd /app

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 6.2 Container Registry Authentication

```bash
# Create GitHub token for package registry
# Go to Settings → Developer settings → Personal access tokens → Generate new token
# Scopes: read:packages, write:packages

# Login to container registry
docker login ghcr.io -u your-username -p your-token
```

#### 6.3 Configure Deployment Script

Create `deploy.sh` on production server:

```bash
#!/bin/bash
set -e

cd /app
docker-compose pull
docker-compose up -d

echo "✅ Deployment completed at $(date)"
```

Make executable:
```bash
chmod +x deploy.sh
```

---

### Phase 7: Testing the Complete Pipeline

#### 7.1 Full Integration Test

1. Create branch: `feature/test-integration`
2. Make changes to multiple files
3. Create PR
4. Observe:
   - Security scan runs
   - Dependency scan runs
   - LangSmith review runs
   - Tests pass
   - Email approval sent
5. Check email and approve
6. Merge PR
7. Watch deployment occur

#### 7.2 Verify Deployment

```bash
# On production server
docker-compose ps
docker-compose logs api

# Test API
curl http://your-server.com:8000/health
```

---

### Phase 8: Monitoring & Maintenance

#### 8.1 Setup Monitoring

```bash
# Check logs
docker-compose logs -f api

# Monitor resource usage
docker stats

# View application metrics
curl http://your-server.com:8000/health
```

#### 8.2 Backup Configuration

```bash
# Backup .env file (never commit)
cp .env /secure/backup/.env.$(date +%Y%m%d)

# Backup uploads directory
docker-compose exec api tar czf - uploads/ | gzip > uploads-backup-$(date +%Y%m%d).tar.gz
```

#### 8.3 Regular Maintenance

- Monitor email approval requests
- Review GitHub Actions logs
- Check security scan results
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review LangSmith insights

---

## Troubleshooting

### Email Not Sending

```bash
# Check SMTP configuration
curl -X POST http://localhost:8000/test-email

# Verify credentials
echo "Testing SMTP connection..."
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'app-password')
print('✅ SMTP connection successful')
"
```

### LangSmith API Issues

```bash
# Test LangSmith connection
python -c "
from langsmith import Client
client = Client(api_key='your-key')
print('✅ LangSmith connected')
"
```

### GitHub Actions Failures

1. Check workflow logs in Actions tab
2. Verify all secrets are set
3. Check branch protection rules
4. Review YAML syntax

### Docker Issues

```bash
# Rebuild image
docker-compose build --no-cache

# Check image layers
docker history file-check:latest

# Clean up
docker system prune -a
```

---

## Quick Commands Reference

```bash
# Development
uvicorn app.main:app --reload

# Testing
pytest tests/ -v --cov=app

# Code quality
black app/ langsmith_agent/
isort app/ langsmith_agent/
pylint app/ langsmith_agent/

# Docker
docker-compose up --build
docker-compose down
docker-compose logs -f

# Git
git branch -a
git log --oneline
git diff main
```

---

## Success Indicators

✅ All phases completed when you see:
- Local tests passing
- GitHub Actions workflows running
- Approval emails being received
- Successful PR merge workflow
- Container deployed to production
- API responding on production server

---

## Support

For issues:
1. Check logs: `docker-compose logs api`
2. Review GitHub Actions execution
3. Check LangSmith dashboard
4. Review email configuration

