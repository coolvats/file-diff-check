"""Tests for file utilities"""

import pytest
import tempfile
from pathlib import Path
import hashlib

from app.utils.file_utils import (
    calculate_file_hash,
    check_file_duplicates,
    compare_file_hashes,
    get_file_info
)


@pytest.fixture
def temp_files():
    """Create temporary test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create identical files
        file1 = tmpdir_path / "file1.txt"
        file2 = tmpdir_path / "file2.txt"
        content = b"test content"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        
        # Create different file
        file3 = tmpdir_path / "file3.txt"
        file3.write_bytes(b"different content")
        
        yield {
            "file1": str(file1),
            "file2": str(file2),
            "file3": str(file3),
            "tmpdir": str(tmpdir_path)
        }


def test_calculate_file_hash(temp_files):
    """Test file hash calculation"""
    hash1 = calculate_file_hash(temp_files["file1"])
    hash2 = calculate_file_hash(temp_files["file2"])
    hash3 = calculate_file_hash(temp_files["file3"])
    
    # Identical files should have same hash
    assert hash1 == hash2
    # Different files should have different hash
    assert hash1 != hash3
    # Hash should be 64 characters (SHA256)
    assert len(hash1) == 64


def test_compare_file_hashes(temp_files):
    """Test file hash comparison"""
    assert compare_file_hashes(temp_files["file1"], temp_files["file2"]) == True
    assert compare_file_hashes(temp_files["file1"], temp_files["file3"]) == False


def test_check_file_duplicates(temp_files):
    """Test duplicate file detection"""
    hash1 = calculate_file_hash(temp_files["file1"])
    duplicates = check_file_duplicates(hash1, temp_files["tmpdir"])
    
    # Should find at least 2 duplicates (file1 and file2)
    assert len(duplicates) >= 2
    
    # All should have same hash
    for dup in duplicates:
        assert dup["hash"] == hash1


def test_get_file_info(temp_files):
    """Test getting file information"""
    info = get_file_info(temp_files["file1"])
    
    assert info["name"] == "file1.txt"
    assert info["size"] > 0
    assert info["extension"] == ".txt"
    assert info["is_file"] == True
    assert info["hash"] is not None


def test_nonexistent_file():
    """Test handling of nonexistent files"""
    with pytest.raises(FileNotFoundError):
        calculate_file_hash("/nonexistent/file.txt")
    
    with pytest.raises(FileNotFoundError):
        get_file_info("/nonexistent/file.txt")
