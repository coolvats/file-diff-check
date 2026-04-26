# QUICKSTART.md - Get Started in 5 Minutes

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Git
- Docker (optional, for production)

---

## ⚡ 5-Minute Local Setup

### Step 1: Clone & Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/your-username/file-check.git
cd file-check

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# For local development, you can use defaults or edit .env
# Minimal required for local testing:
# ENVIRONMENT=development
# HOST=0.0.0.0
# PORT=8000
```

### Step 3: Run Application (2 minutes)

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

**Server running!** Visit:
- 🌐 API: http://localhost:8000
- 📖 Docs: http://localhost:8000/docs
- 🔍 ReDoc: http://localhost:8000/redoc

---

## 🧪 Test the API (in another terminal)

### Upload a File

```bash
# Create a test file
echo "test content" > test.txt

# Upload it
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test.txt"

# Response example:
# {
#   "filename": "test.txt",
#   "file_hash": "6ae8a75555209fd6c44157c0aed8016e",
#   "size": 12,
#   "uploaded_at": "2024-01-15T...",
#   "message": "File test.txt uploaded successfully"
# }
```

### Check for Duplicates

```bash
# Replace with hash from upload response
FILE_HASH="6ae8a75555209fd6c44157c0aed8016e"

curl http://localhost:8000/api/files/check/${FILE_HASH}

# Response:
# {
#   "is_duplicate": false,
#   "file_hash": "6ae8a75555209fd6c44157c0aed8016e",
#   "duplicates": [],
#   "timestamp": "2024-01-15T..."
# }
```

### Health Check

```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T...",
#   "version": "1.0.0",
#   "environment": "development"
# }
```

---

## ✅ Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## 🐳 Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# API available at: http://localhost:8000

# Stop containers
docker-compose down
```

---

## 📚 Next Steps

### For Development

1. **Read Full Documentation**
   - 📖 See [README.md](README.md)
   - 🔧 See [SETUP_GUIDE.md](SETUP_GUIDE.md)
   - 📡 See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

2. **Make Changes**
   ```bash
   # Create new branch
   git checkout -b feature/my-feature
   
   # Make changes and test
   pytest tests/ -v
   
   # Commit and push
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-feature
   ```

3. **Code Quality**
   ```bash
   # Format code
   black app/ langsmith_agent/ scripts/
   
   # Sort imports
   isort app/ langsmith_agent/ scripts/
   
   # Lint
   pylint app/
   ```

### For Production Deployment

1. **Setup GitHub Repository**
   - Create repo on GitHub
   - Push code
   - Configure secrets
   - See [SETUP_GUIDE.md Phase 3](SETUP_GUIDE.md)

2. **Configure CI/CD**
   - Add secrets (LangSmith, Gmail, GitHub)
   - Test PR review workflow
   - See [CICD_WORKFLOW.md](CICD_WORKFLOW.md)

3. **Deploy**
   - Create PR
   - Approve via email
   - Merge
   - Watch deployment
   - See [SETUP_GUIDE.md Phase 6](SETUP_GUIDE.md)

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| API Docs (Local) | http://localhost:8000/docs |
| ReDoc (Local) | http://localhost:8000/redoc |
| GitHub | https://github.com/your-username/file-check |
| LangSmith | https://smith.langchain.com |
| FastAPI Docs | https://fastapi.tiangolo.com |

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Python Not Found

```bash
# Use full path to Python 3.11
/usr/local/bin/python3.11 -m venv venv

# Or install Python 3.11:
# macOS: brew install python@3.11
# Windows: https://www.python.org/downloads/
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clear cache
pip cache purge
```

### Permission Denied

```bash
# macOS/Linux
chmod +x venv/bin/activate

# Or use full path
source ./venv/bin/activate
```

---

## 📞 Getting Help

- 📖 Check [README.md](README.md)
- 🔧 Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 📡 Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- 💬 Open GitHub Issue
- ✉️ Email: vatsalyamishra93@gmail.com

---

## ✨ Key Features

✅ File duplicate detection using SHA256 hashing  
✅ FastAPI with automatic API documentation  
✅ GitHub Actions CI/CD pipeline  
✅ LangSmith intelligent code review  
✅ Email-based approval workflow  
✅ Security scanning (Bandit, Safety)  
✅ Dependency vulnerability scanning  
✅ Docker containerization  
✅ Comprehensive testing  
✅ Production-ready  

---

**Happy coding! 🎉**

