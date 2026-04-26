# File Duplicate Checker API - GitHub CI/CD Pipeline

Intelligent API for detecting duplicate files using content-based hashing with automated CI/CD pipeline powered by LangSmith fleet agent for code review and email-based deployment approvals.

## Features

- 🔍 **File Duplicate Detection**: SHA256 hash-based file comparison
- 🤖 **LangSmith Fleet Agent**: Intelligent code review and analysis
- 📧 **Email Approval System**: Automated approval workflows
- 🔐 **Security Scanning**: Bandit and Safety integration
- 📦 **Dependency Scanning**: Automated dependency vulnerability checks
- 🚀 **GitHub Actions CI/CD**: Complete automated pipeline
- 🐳 **Docker Support**: Production-ready containerization
- ✅ **Comprehensive Testing**: Unit and integration tests

## Architecture

```
┌─────────────────┐
│  GitHub PR      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  GitHub Actions Workflow (pr-review.yml)    │
├─────────────────────────────────────────────┤
│ • Security Scan (Bandit)                    │
│ • Dependency Scan (Safety, pip-audit)       │
│ • LangSmith Code Review                     │
│ • Automated Tests (pytest)                  │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  LangSmith Fleet Agent                      │
├─────────────────────────────────────────────┤
│ • Analyzes code changes                     │
│ • Reviews security findings                 │
│ • Checks dependencies                       │
│ • Generates recommendations                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Email Approval Request                     │
├─────────────────────────────────────────────┤
│ • Sends to: vatsalyamishra93@gmail.com      │
│ • Includes: Issues, recommendations         │
│ • Contains: Approval/rejection link         │
└────────┬────────────────────────────────────┘
         │
    [Approve] [Reject]
         │
         ▼
┌─────────────────────────────────────────────┐
│  Deployment Workflow (deploy.yml)           │
├─────────────────────────────────────────────┤
│ • Build Docker image                        │
│ • Push to registry                          │
│ • Deploy to production                      │
│ • Send deployment status                    │
└─────────────────────────────────────────────┘
```

## Project Structure

```
file-check/
├── app/
│   ├── main.py                 # FastAPI main application
│   ├── config.py               # Configuration settings
│   ├── models.py               # Pydantic models
│   ├── routes/
│   │   ├── file_routes.py      # File checking endpoints
│   │   └── health_routes.py    # Health check endpoints
│   └── utils/
│       ├── file_utils.py       # File hashing utilities
│       ├── logger.py           # Logging setup
│       └── email_notifier.py   # Email notifications
├── langsmith_agent/
│   ├── code_review_agent.py    # LangSmith integration
│   └── github_integration.py    # GitHub API integration
├── scripts/
│   ├── run_code_review.py      # Code review script
│   └── send_approval_email.py  # Email approval script
├── tests/
│   ├── test_file_utils.py      # File utility tests
│   └── test_routes.py          # API route tests
├── .github/
│   └── workflows/
│       ├── pr-review.yml       # PR review workflow
│       └── deploy.yml          # Deployment workflow
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── pyproject.toml
├── .env.example
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- GitHub account
- LangSmith account
- Gmail account (or other SMTP provider)

### Local Development

1. **Clone the repository**

```bash
git clone <repository-url>
cd file-check
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the application**

```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up --build
```

## API Endpoints

### File Operations

#### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "filename": "document.pdf",
  "file_hash": "abc123...",
  "size": 1024,
  "uploaded_at": "2024-01-01T12:00:00",
  "message": "File uploaded successfully"
}
```

#### Check File for Duplicates
```http
GET /api/files/check/{file_hash}?compare_directory=/path/to/files
```

**Response:**
```json
{
  "is_duplicate": true,
  "file_hash": "abc123...",
  "duplicates": [
    {
      "path": "/path/to/duplicate1.pdf",
      "hash": "abc123..."
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

#### Compare Two Files
```http
POST /api/files/compare?file1_path=/path/file1.txt&file2_path=/path/file2.txt
```

**Response:**
```json
{
  "file1_hash": "hash1...",
  "file2_hash": "hash1...",
  "are_duplicates": true,
  "file1_path": "/path/file1.txt",
  "file2_path": "/path/file2.txt"
}
```

#### Batch Check Files
```http
POST /api/files/batch-check
Content-Type: application/json

{
  "file_paths": [
    "/path/file1.txt",
    "/path/file2.txt"
  ]
}
```

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "environment": "production"
}
```

## GitHub Actions CI/CD Setup

### 1. Add Secrets to GitHub

Go to **Settings → Secrets and variables → Actions** and add:

```
LANGSMITH_API_KEY          # LangSmith API key
GITHUB_TOKEN               # GitHub token (auto-provided)
SMTP_SERVER                # SMTP server (e.g., smtp.gmail.com)
SMTP_PORT                  # SMTP port (e.g., 587)
SMTP_USERNAME              # Email account username
SMTP_PASSWORD              # Email app password
APPROVAL_EMAIL             # Email for approvals
DEPLOYMENT_KEY             # SSH key for deployment
DEPLOYMENT_HOST            # Deployment server host
DEPLOYMENT_USER            # Deployment user
SLACK_WEBHOOK              # Slack webhook (optional)
```

### 2. Email Setup (Gmail Example)

1. Enable 2-Factor Authentication
2. Generate App Password at https://myaccount.google.com/apppasswords
3. Use app password in `SMTP_PASSWORD`

### 3. Workflow Triggers

- **PR Review Workflow**: Triggers on PR open/sync/reopen
- **Deployment Workflow**: Triggers on PR merge

## LangSmith Integration

### Configuration

1. **Get API Key**
   - Sign up at https://smith.langchain.com
   - Generate API key from settings

2. **Set Environment Variables**
   ```bash
   export LANGSMITH_API_KEY="your-api-key"
   export LANGSMITH_PROJECT="file-duplicate-checker"
   ```

3. **Features**
   - Intelligent code review analysis
   - Security issue assessment
   - Dependency vulnerability review
   - Recommendations generation
   - Approval workflow integration

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_file_utils.py::test_calculate_file_hash -v
```

## Security Scanning

### Manual Security Scan

```bash
# Bandit (Python security)
bandit -r app/

# Safety (Dependency vulnerabilities)
safety check

# pip-audit
pip-audit
```

## Deployment

### Production Deployment Steps

1. **Push code to main branch**
2. **Create Pull Request** - triggers pr-review.yml
3. **Code Review** - LangSmith analyzes changes
4. **Email Approval** - Approval email sent to configured address
5. **Review & Approve** - Click approval link in email
6. **Merge PR** - Triggers deploy.yml workflow
7. **Build & Deploy** - Docker image built and deployed

### Manual Deployment

```bash
# Build image
docker build -t file-check:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LANGSMITH_API_KEY=$LANGSMITH_API_KEY \
  file-check:latest
```

## Configuration

### Application Settings

Edit `app/config.py` or `.env` file:

```env
# API
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600  # 100 MB

# LangSmith
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=file-duplicate-checker

# Email
APPROVAL_EMAIL=vatsalyamishra93@gmail.com

# GitHub
GITHUB_REPO=your/repo
```

## Monitoring & Logging

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General information messages
- `WARNING`: Warning messages
- `ERROR`: Error messages

### View Logs

```bash
# Docker logs
docker-compose logs -f api

# Application logs
tail -f app.log
```

## Troubleshooting

### Email Not Sending

1. Verify SMTP credentials
2. Check firewall/network settings
3. Review email logs in GitHub Actions
4. Verify Gmail app password (not regular password)

### LangSmith Integration Issues

1. Verify API key is correct
2. Check project name configuration
3. Review LangSmith dashboard for errors

### GitHub Actions Failures

1. Check GitHub Actions logs
2. Verify all secrets are configured
3. Review workflow YAML syntax
4. Check branch protection rules

## Development

### Code Style

```bash
# Format code
black app/ langsmith_agent/ scripts/

# Sort imports
isort app/ langsmith_agent/ scripts/

# Lint
pylint app/ langsmith_agent/

# Type checking
mypy app/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/name`
2. Make changes
3. Add tests
4. Run tests: `pytest`
5. Push and create PR
6. Review and approval process automatically runs

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support & Issues

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with details
3. Contact: vatsalyamishra93@gmail.com

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Changelog

### Version 1.0.0 (Initial Release)
- File duplicate detection API
- GitHub Actions CI/CD pipeline
- LangSmith code review integration
- Email approval workflow
- Security & dependency scanning
