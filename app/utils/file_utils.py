"""File utility functions"""

import hashlib
from pathlib import Path
from typing import List, Dict
import os
import logging

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate the hash of a file
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
    
    Returns:
        Hex digest of the file hash
    """
    hasher = hashlib.new(algorithm)
    
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(65536)  # 64kb chunks
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {str(e)}")
        raise


def check_file_duplicates(
    file_hash: str,
    search_directory: str = None,
    exclude_path: str = None
) -> List[Dict[str, str]]:
    """
    Check for duplicate files with the same hash
    
    Args:
        file_hash: Hash to search for
        search_directory: Directory to search in (default: current directory)
        exclude_path: Path to exclude from search
    
    Returns:
        List of duplicate file paths and their hashes
    """
    duplicates = []
    search_dir = Path(search_directory or ".")
    
    if not search_dir.exists():
        logger.warning(f"Search directory does not exist: {search_dir}")
        return duplicates
    
    try:
        for file_path in search_dir.rglob("*"):
            if file_path.is_file():
                if exclude_path and str(file_path) == exclude_path:
                    continue
                
                try:
                    file_hash_value = calculate_file_hash(str(file_path))
                    if file_hash_value == file_hash:
                        duplicates.append({
                            "path": str(file_path),
                            "hash": file_hash_value
                        })
                except Exception as e:
                    logger.warning(f"Could not hash file {file_path}: {str(e)}")
                    continue
    
    except Exception as e:
        logger.error(f"Error searching directory {search_dir}: {str(e)}")
    
    return duplicates


def compare_file_hashes(file_path1: str, file_path2: str) -> bool:
    """
    Compare two files by their hashes
    
    Args:
        file_path1: Path to first file
        file_path2: Path to second file
    
    Returns:
        True if files are identical, False otherwise
    """
    try:
        hash1 = calculate_file_hash(file_path1)
        hash2 = calculate_file_hash(file_path2)
        return hash1 == hash2
    except Exception as e:
        logger.error(f"Error comparing files: {str(e)}")
        raise


def get_file_info(file_path: str) -> Dict[str, any]:
    """
    Get comprehensive file information
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat = path.stat()
    
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "size": stat.st_size,
        "extension": path.suffix,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "is_file": path.is_file(),
        "hash": calculate_file_hash(file_path) if path.is_file() else None
    }
