"""Tests for API routes"""

import pytest
from fastapi.testclient import TestClient
import tempfile
from pathlib import Path

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "docs" in data


def test_readiness_check():
    """Test readiness check endpoint"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] == True


def test_upload_file():
    """Test file upload endpoint"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        f.flush()
        temp_path = f.name
    
    try:
        with open(temp_path, "rb") as f:
            response = client.post(
                "/api/files/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert "file_hash" in data
        assert data["size"] > 0
    finally:
        Path(temp_path).unlink()


def test_check_file():
    """Test file check endpoint"""
    # Create a test file and get its hash
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content")
        f.flush()
        temp_path = f.name
    
    try:
        # Upload file first
        with open(temp_path, "rb") as f:
            upload_response = client.post(
                "/api/files/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        file_hash = upload_response.json()["file_hash"]
        
        # Check file
        response = client.get(f"/api/files/check/{file_hash}")
        assert response.status_code == 200
        data = response.json()
        assert data["file_hash"] == file_hash
        assert "is_duplicate" in data
    finally:
        Path(temp_path).unlink()


def test_compare_files():
    """Test file comparison endpoint"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two identical files
        file1 = Path(tmpdir) / "file1.txt"
        file2 = Path(tmpdir) / "file2.txt"
        content = "test content"
        
        file1.write_text(content)
        file2.write_text(content)
        
        # Compare files
        response = client.post(
            "/api/files/compare",
            params={
                "file1_path": str(file1),
                "file2_path": str(file2)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["are_duplicates"] == True
        assert data["file1_hash"] == data["file2_hash"]
