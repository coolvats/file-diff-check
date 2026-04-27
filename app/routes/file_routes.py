# File checking routes

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pathlib import Path
import hashlib
import aiofiles
import os
from typing import List, Dict
import logging

from app.models import FileCheckResponse, UploadResponse, ComparisonResult
from app.config import settings
from app.utils.file_utils import calculate_file_hash, check_file_duplicates
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a file and calculate its hash
    
    Args:
        file: File to upload
        background_tasks: Background tasks for async operations
    
    Returns:
        UploadResponse with file hash and metadata
    """
    try:
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Calculate hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Save file
        file_path = Path(settings.UPLOAD_DIR) / f"{file_hash}_{file.filename}"
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        logger.info(f"File uploaded: {file.filename}, Hash: {file_hash}")
        
        return UploadResponse(
            filename=file.filename,
            file_hash=file_hash,
            size=file_size,
            message=f"File {file.filename} uploaded successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error uploading file")


@router.get("/check/{file_hash}", response_model=FileCheckResponse)
async def check_file(file_hash: str, compare_directory: str = None):
    """
    Check if a file with given hash already exists (indicating a duplicate)
    
    Args:
        file_hash: SHA256 hash of the file
        compare_directory: Optional directory to compare against
    
    Returns:
        FileCheckResponse with duplicate status
    """
    try:
        duplicates = check_file_duplicates(file_hash, compare_directory)
        
        logger.info(f"File check for hash {file_hash}: {len(duplicates)} duplicates found")
        
        return FileCheckResponse(
            is_duplicate=len(duplicates) > 0,
            file_hash=file_hash,
            duplicates=duplicates
        )
    
    except Exception as e:
        logger.error(f"Error checking file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking file")


@router.post("/compare", response_model=ComparisonResult)
async def compare_files(file1_path: str, file2_path: str):
    """
    Compare two files to check if they are duplicates
    
    Args:
        file1_path: Path to first file
        file2_path: Path to second file
    
    Returns:
        ComparisonResult with comparison details
    """
    try:
        # Validate file paths
        file1 = Path(file1_path)
        file2 = Path(file2_path)
        
        if not file1.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file1_path}")
        if not file2.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file2_path}")
        
        # Calculate hashes
        hash1 = calculate_file_hash(file1_path)
        hash2 = calculate_file_hash(file2_path)
        
        are_duplicates = hash1 == hash2
        
        logger.info(f"File comparison: {file1_path} vs {file2_path}, Duplicates: {are_duplicates}")
        
        return ComparisonResult(
            file1_hash=hash1,
            file2_hash=hash2,
            are_duplicates=are_duplicates,
            file1_path=file1_path,
            file2_path=file2_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing files: {str(e)}")
        raise HTTPException(status_code=500, detail="Error comparing files")


@router.post("/batch-check")
async def batch_check_files(file_paths: List[str]):
    """
    Check multiple files for duplicates
    
    Args:
        file_paths: List of file paths to check
    
    Returns:
        List of file check results
    """
    try:
        results = []
        for file_path in file_paths:
            try:
                if not Path(file_path).exists():
                    results.append({
                        "file_path": file_path,
                        "error": "File not found",
                        "is_duplicate": None
                    })
                    continue
                
                file_hash = calculate_file_hash(file_path)
                duplicates = check_file_duplicates(file_hash)
                
                results.append({
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "is_duplicate": len(duplicates) > 0,
                    "duplicate_count": len(duplicates)
                })
            except Exception as e:
                logger.error(f"Error checking file {file_path}: {str(e)}")
                results.append({
                    "file_path": file_path,
                    "error": str(e)
                })
        
        return {"total": len(file_paths), "results": results}
    
    except Exception as e:
        logger.error(f"Error in batch check: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in batch check")