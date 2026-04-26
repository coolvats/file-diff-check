# API_DOCUMENTATION.md - Detailed API Reference

## API Reference Documentation

### Base URL
```
http://localhost:8000  (Development)
https://api.your-domain.com  (Production)
```

### Authentication
Currently no authentication required. Recommended to add in production.

---

## File Operations

### 1. Upload File

Upload a file and receive its hash for duplicate checking.

**Endpoint:**
```http
POST /api/files/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): Binary file content

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/document.pdf"
```

**Response (200):**
```json
{
  "filename": "document.pdf",
  "file_hash": "5d41402abc4b2a76b9719d911017c592",
  "size": 1024,
  "uploaded_at": "2024-01-15T10:30:00",
  "message": "File document.pdf uploaded successfully"
}
```

**Response (413):**
```json
{
  "detail": "File too large. Max size: 104857600 bytes"
}
```

---

### 2. Check File for Duplicates

Check if a file (by hash) already exists and get duplicate locations.

**Endpoint:**
```http
GET /api/files/check/{file_hash}
```

**Parameters:**
- `file_hash` (required, path): SHA256 hash of the file
- `compare_directory` (optional, query): Directory to search for duplicates

**Example Request:**
```bash
curl http://localhost:8000/api/files/check/5d41402abc4b2a76b9719d911017c592?compare_directory=/home/user/documents
```

**Response (200):**
```json
{
  "is_duplicate": true,
  "file_hash": "5d41402abc4b2a76b9719d911017c592",
  "duplicates": [
    {
      "path": "/home/user/documents/copy1.pdf",
      "hash": "5d41402abc4b2a76b9719d911017c592"
    },
    {
      "path": "/home/user/downloads/backup.pdf",
      "hash": "5d41402abc4b2a76b9719d911017c592"
    }
  ],
  "timestamp": "2024-01-15T10:31:00"
}
```

---

### 3. Compare Two Files

Compare two specific files to check if they are identical.

**Endpoint:**
```http
POST /api/files/compare
```

**Query Parameters:**
- `file1_path` (required): Path to first file
- `file2_path` (required): Path to second file

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/files/compare \
  -G -d file1_path=/path/to/file1.txt \
  -d file2_path=/path/to/file2.txt
```

**Response (200):**
```json
{
  "file1_hash": "5d41402abc4b2a76b9719d911017c592",
  "file2_hash": "5d41402abc4b2a76b9719d911017c592",
  "are_duplicates": true,
  "file1_path": "/path/to/file1.txt",
  "file2_path": "/path/to/file2.txt"
}
```

**Response (404):**
```json
{
  "detail": "File not found: /path/to/file.txt"
}
```

---

### 4. Batch Check Files

Check multiple files for duplicates in a single request.

**Endpoint:**
```http
POST /api/files/batch-check
Content-Type: application/json
```

**Request Body:**
```json
{
  "file_paths": [
    "/path/to/file1.txt",
    "/path/to/file2.txt",
    "/path/to/file3.txt"
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/files/batch-check \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": [
      "/home/user/doc1.pdf",
      "/home/user/doc2.pdf"
    ]
  }'
```

**Response (200):**
```json
{
  "total": 3,
  "results": [
    {
      "file_path": "/path/to/file1.txt",
      "file_hash": "hash1...",
      "is_duplicate": false,
      "duplicate_count": 0
    },
    {
      "file_path": "/path/to/file2.txt",
      "file_hash": "hash2...",
      "is_duplicate": true,
      "duplicate_count": 1
    },
    {
      "file_path": "/path/to/file3.txt",
      "error": "File not found"
    }
  ]
}
```

---

## Health & Monitoring

### 1. Health Check

Check if the API is running and healthy.

**Endpoint:**
```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:32:00",
  "version": "1.0.0",
  "environment": "production"
}
```

---

### 2. Readiness Check

Check if the API is ready to handle requests.

**Endpoint:**
```http
GET /health/ready
```

**Response (200):**
```json
{
  "ready": true,
  "timestamp": "2024-01-15T10:32:00"
}
```

---

## Error Responses

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | File or resource not found |
| 413 | Payload Too Large | File exceeds maximum size |
| 500 | Internal Server Error | Server error |

### Error Examples

**Invalid File Path:**
```json
{
  "detail": "File not found: /nonexistent/file.txt"
}
```

**File Too Large:**
```json
{
  "detail": "File too large. Max size: 104857600 bytes"
}
```

**Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting applied. Recommended to add in production:

```python
# Install slowapi
pip install slowapi

# Apply rate limiting (10 requests per minute)
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

---

## Data Models

### FileCheckResponse

```python
{
  "is_duplicate": bool,           # Whether file is a duplicate
  "file_hash": str,               # SHA256 hash of the file
  "duplicates": [
    {
      "path": str,                # Path to duplicate file
      "hash": str                 # Hash of duplicate
    }
  ],
  "timestamp": datetime            # When check was performed
}
```

### ComparisonResult

```python
{
  "file1_hash": str,              # Hash of first file
  "file2_hash": str,              # Hash of second file
  "are_duplicates": bool,         # Whether files are identical
  "file1_path": str,              # Path to first file
  "file2_path": str               # Path to second file
}
```

### UploadResponse

```python
{
  "filename": str,                # Original filename
  "file_hash": str,               # SHA256 hash
  "size": int,                    # File size in bytes
  "uploaded_at": datetime,        # Upload timestamp
  "message": str                  # Status message
}
```

---

## Code Examples

### Python

```python
import requests

# Upload file
with open('/path/to/file.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/files/upload', files=files)
    result = response.json()
    file_hash = result['file_hash']

# Check for duplicates
response = requests.get(
    f'http://localhost:8000/api/files/check/{file_hash}',
    params={'compare_directory': '/home/user/documents'}
)
duplicates = response.json()

if duplicates['is_duplicate']:
    print(f"Found {len(duplicates['duplicates'])} duplicates")
    for dup in duplicates['duplicates']:
        print(f"  - {dup['path']}")
```

### JavaScript

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/files/upload', {
  method: 'POST',
  body: formData
});
const uploadData = await uploadResponse.json();
const fileHash = uploadData.file_hash;

// Check for duplicates
const checkResponse = await fetch(
  `http://localhost:8000/api/files/check/${fileHash}`
);
const checkData = await checkResponse.json();

if (checkData.is_duplicate) {
  console.log(`Found ${checkData.duplicates.length} duplicates`);
}
```

### cURL

```bash
# Upload file
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/file.pdf"

# Get file hash from response and check duplicates
curl http://localhost:8000/api/files/check/5d41402abc4b2a76b9719d911017c592 \
  -G -d compare_directory=/home/user/documents

# Compare two files
curl -X POST http://localhost:8000/api/files/compare \
  -G -d file1_path=/path/to/file1.txt \
  -d file2_path=/path/to/file2.txt
```

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

