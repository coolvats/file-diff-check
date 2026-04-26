# CICD_WORKFLOW.md - Complete CI/CD Pipeline Documentation

## GitHub Actions CI/CD Pipeline Overview

### Architecture Diagram

```
GitHub PR Event
    │
    ├─→ [Security Scan Job]
    │    ├─ Install dependencies
    │    ├─ Run Bandit (Python security)
    │    └─ Run Safety (Dependency vulnerabilities)
    │
    ├─→ [Dependency Scan Job]
    │    ├─ Install dependencies
    │    └─ Run pip-audit
    │
    ├─→ [Tests Job]
    │    ├─ Install dependencies
    │    ├─ Run pytest
    │    └─ Generate coverage report
    │
    ├─→ [LangSmith Review Job] (waits for security & dependency scans)
    │    ├─ Download scan reports
    │    ├─ Run code review agent
    │    ├─ Generate recommendations
    │    └─ Upload review results
    │
    └─→ [Approval Request Job] (waits for review & tests)
         ├─ Send approval email
         └─ Comment on PR

    ↓ [Manual Approval from Email]

    ├─→ [PR Merge Event]
    │
    └─→ [Deploy Workflow]
         ├─ Check approval status
         ├─ Build Docker image
         ├─ Push to registry
         ├─ Deploy to production
         └─ Send notification
```

---

## Workflow Files

### 1. pr-review.yml - Pull Request Review Workflow

**Trigger:** `pull_request` (opened, synchronize, reopened)

**Jobs:**

#### security-scan
- Runs Bandit for Python security issues
- Generates JSON report
- Uploads artifacts

#### dependency-scan
- Runs pip-audit for dependency vulnerabilities
- Generates JSON report
- Uploads artifacts

#### langsmith-review (depends on: security-scan, dependency-scan)
- Runs LangSmith code review agent
- Analyzes changed files
- Generates review report
- Checks for approval requirements

#### tests
- Runs pytest suite
- Generates coverage report
- Uploads to Codecov

#### approval-request (depends on: langsmith-review, tests)
- Sends approval request email
- Comments on PR with summary
- Includes security & dependency findings

**Environment Variables:**
```yaml
REGISTRY: ghcr.io
IMAGE_NAME: ${{ github.repository }}
```

---

### 2. deploy.yml - Deployment Workflow

**Trigger:** 
- `pull_request` closed (merged)
- Manual: `workflow_dispatch`

**Jobs:**

#### check-approval
- Verifies PR is merged
- Confirms approval status

#### build-and-push
- Sets up Docker Buildx
- Logs into container registry
- Builds Docker image
- Pushes to registry with tags

#### deploy
- Deploys to production server
- Runs deployment script via SSH
- Sends Slack notification

**Secrets Required:**
```
DEPLOYMENT_KEY       - SSH private key
DEPLOYMENT_HOST      - Server hostname/IP
DEPLOYMENT_USER      - SSH username
SLACK_WEBHOOK        - Slack notification webhook
```

---

## Configuration Files

### GitHub Secrets

Add these secrets to: **Settings → Secrets and variables → Actions**

```yaml
# Code Review & Scanning
LANGSMITH_API_KEY         # LangSmith API key

# Email Configuration
SMTP_SERVER              # SMTP server (smtp.gmail.com)
SMTP_PORT                # SMTP port (587)
SMTP_USERNAME            # Email account
SMTP_PASSWORD            # App password (not regular password)
APPROVAL_EMAIL           # Approval recipient

# Deployment
DEPLOYMENT_KEY           # SSH private key (cat ~/.ssh/id_rsa)
DEPLOYMENT_HOST          # Server IP/hostname
DEPLOYMENT_USER          # SSH username

# Notifications (Optional)
SLACK_WEBHOOK            # Slack webhook for notifications
```

### Environment Variables

Set in `.env` file for local development:

```bash
# API
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600

# LangSmith
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=file-duplicate-checker

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-password
APPROVAL_EMAIL=vatsalyamishra93@gmail.com

# GitHub
GITHUB_TOKEN=your-token
GITHUB_REPO=your-repo
GITHUB_OWNER=your-username
```

---

## Workflow Execution Flow

### 1. Developer Creates Pull Request

```bash
git checkout -b feature/new-feature
# Make changes
git commit -am "Add new feature"
git push origin feature/new-feature
# Create PR on GitHub
```

### 2. GitHub Actions PR Workflow Triggers

**Parallel Execution:**
```
Time 0:00 → All jobs start simultaneously
├─ security-scan (3-5 minutes)
├─ dependency-scan (2-3 minutes)
└─ tests (5-10 minutes)

Time 5:00 → Security & Dependency scans complete
├─ langsmith-review starts (depends on above)
│   └─ Analyzes code (2-3 minutes)
└─ approval-request queued

Time 8:00 → All jobs complete
└─ approval-request sends email
   └─ Comment posted to PR
```

### 3. LangSmith Code Review Analysis

**Process:**
1. Loads security scan results (Bandit)
2. Loads dependency scan results (Safety, pip-audit)
3. Analyzes code changes
4. Generates recommendations
5. Determines approval status
6. Saves review results (review-result.json)

**Review Status Values:**
- `approved` - Safe to deploy
- `needs_changes` - Issues found, approval required
- `rejected` - Critical issues, deployment blocked

### 4. Email Approval Request Sent

**Email Contents:**
- PR number and review ID
- Security issues found
- Dependency vulnerabilities
- Code quality recommendations
- Approval link (approval_url)

**Example Email:**
```
Subject: [ACTION REQUIRED] Code Review Approval Needed - PR #42

PR Number: 42
Review ID: review_abc123

Security Issues Found: 2
  - SQL injection vulnerability in query builder
  - Hardcoded credentials in config

Dependency Issues Found: 1
  - requests library has known CVE

Action Required:
Please review the code changes and approve or reject the deployment.

Approval Link: https://github.com/owner/repo/pull/42?review_id=review_abc123&action=approve

This is an automated message from File Duplicate Checker CI/CD Pipeline.
```

### 5. Approval & Merge

**Option A: Approve via Email Link**
1. Click approval link in email
2. Confirm approval on GitHub
3. Merge PR manually

**Option B: Standard GitHub Merge**
1. Code review approval
2. Merge PR to main

### 6. Deployment Workflow Triggers

**When:** PR merged to main branch

**Deployment Steps:**
1. Check approval status
2. Build Docker image
3. Push to container registry
4. Deploy to production server
5. Send deployment notification

**Production Deployment:**
```bash
# On production server via SSH
docker-compose pull
docker-compose up -d
# Service is now live with new code
```

---

## Monitoring & Logs

### GitHub Actions Logs

**Location:** Repository → Actions tab

**View Workflow:**
1. Click workflow run
2. Click job name
3. Expand steps to see logs
4. Search for errors/warnings

### Local Debugging

**Run workflows locally:**
```bash
# Install act
brew install act  # macOS
# or
choco install act  # Windows

# Run specific workflow
act pull_request -j security-scan
```

### Common Issues & Solutions

#### Email Not Sending
```
Problem: Approval email not received
Solution:
1. Check SMTP credentials in secrets
2. Verify Gmail app password (not regular password)
3. Check spam folder
4. Enable "Less secure app access" (Gmail)
5. Review logs: GitHub Actions → Job logs → "Send approval request email" step
```

#### LangSmith Review Fails
```
Problem: Code review not completed
Solution:
1. Verify LANGSMITH_API_KEY secret
2. Check API key hasn't expired
3. Review LangSmith dashboard for errors
4. Ensure project exists in LangSmith
5. Check logs for API response
```

#### Tests Failing
```
Problem: Pytest fails in CI but passes locally
Solution:
1. Check Python version (should be 3.11)
2. Verify all dependencies installed
3. Check for environment-specific issues
4. Review test logs for specific failures
5. Run same tests locally: pytest -v
```

#### Docker Build Fails
```
Problem: Docker build error in deploy workflow
Solution:
1. Verify Dockerfile syntax
2. Check all dependencies in requirements.txt
3. Review Docker build logs
4. Test build locally: docker build -t test .
5. Check registry credentials
```

---

## Security Considerations

### Secrets Management

✅ **Best Practices:**
- Never commit `.env` file
- Rotate secrets regularly
- Use unique passwords for each service
- Use GitHub secrets for sensitive data
- Enable secret scanning in GitHub

❌ **Avoid:**
- Hardcoding secrets in workflows
- Committing credentials to git
- Sharing secrets in PRs or comments
- Using personal passwords

### Scan Results

**Bandit:** Identifies Python security issues
- SQL injection
- Hardcoded passwords
- Insecure deserialization
- etc.

**Safety:** Checks dependency vulnerabilities
- Known CVEs in dependencies
- Outdated library versions

**pip-audit:** Additional dependency checks
- Broader vulnerability database
- License compliance

---

## Customization

### Add Additional Scanning Tools

**Example: Add SAST scanning**
```yaml
- name: Run SonarQube scan
  uses: SonarSource/sonarcloud-github-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Add Notifications

**Example: Add Slack notification**
```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment completed for PR #${{ github.event.pull_request.number }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Add Deployment Stages

**Example: Add staging deployment**
```yaml
- name: Deploy to staging
  if: github.ref == 'refs/heads/main'
  run: |
    ssh ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }} \
    'cd /staging && docker-compose pull && docker-compose up -d'
```

---

## Performance Optimization

### Parallel Job Execution

Current workflow runs jobs in parallel where possible:
- Security scan (3-5 min)
- Dependency scan (2-3 min)
- Tests (5-10 min)
- Total: ~10 min (parallel)

### Caching Dependencies

Add to workflows to speed up:
```yaml
- name: Cache pip dependencies
  uses: actions/setup-python@v4
  with:
    cache: 'pip'
```

### Matrix Testing

Test against multiple Python versions:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

---

## Troubleshooting Workflow Issues

### Check Workflow Status

```bash
# GitHub CLI
gh run list --repo owner/repo
gh run view RUN_ID
gh run view RUN_ID --log

# Or check web UI
# Repository → Actions → Select workflow
```

### Debug Failed Job

1. Click failed job
2. Expand steps
3. Look for red error messages
4. Check logs for stack traces
5. Reproduce locally if possible

### Common Failures

| Error | Cause | Solution |
|-------|-------|----------|
| Secret not found | Secret not configured | Add to GitHub secrets |
| Permission denied | SSH key invalid | Verify SSH key in secrets |
| Build failed | Dockerfile error | Test build locally |
| Test failed | Test code issue | Run `pytest` locally |
| Email not sent | SMTP error | Check credentials |

---

## Maintenance

### Regular Tasks

- Monitor workflow execution times
- Review security scan results
- Update dependencies regularly
- Rotate SSH keys
- Verify email delivery
- Check disk space on server

### Logs Cleanup

GitHub Actions logs are auto-deleted after 90 days.

### Cost Management

- Monitor CI/CD minutes usage
- Cancel long-running workflows
- Optimize test suite
- Use caching for faster builds

