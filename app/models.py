"""
Data models for the application
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class FileCheckRequest(BaseModel):
    """Request model for file checking"""
    file_path: str = Field(..., description="Path to the file to check")
    compare_with: Optional[List[str]] = Field(
        default=None,
        description="List of file paths to compare with"
    )


class FileCheckResponse(BaseModel):
    """Response model for file checking"""
    is_duplicate: bool = Field(..., description="Whether the file is a duplicate")
    file_hash: str = Field(..., description="SHA256 hash of the file")
    duplicates: List[Dict[str, str]] = Field(
        default=[],
        description="List of duplicate files with their paths and hashes"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class UploadResponse(BaseModel):
    """Response model for file upload"""
    filename: str
    file_hash: str
    size: int
    uploaded_at: datetime = Field(default_factory=datetime.now)
    message: str


class ComparisonResult(BaseModel):
    """Result of file comparison"""
    file1_hash: str
    file2_hash: str
    are_duplicates: bool
    file1_path: str
    file2_path: str


class CodeReviewRequest(BaseModel):
    """Request model for code review from LangSmith"""
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None
    commit_sha: str = Field(..., description="Git commit SHA")
    files_changed: List[str] = Field(..., description="List of changed files")
    security_scan_results: Optional[Dict] = None
    dependency_scan_results: Optional[Dict] = None


class CodeReviewResponse(BaseModel):
    """Response model from LangSmith code review"""
    review_id: str
    status: str  # "approved", "needs_changes", "rejected"
    recommendations: List[str]
    security_issues: List[str] = Field(default=[])
    dependency_issues: List[str] = Field(default=[])
    approval_required: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class ApprovalRequest(BaseModel):
    """Request model for deployment approval"""
    pr_number: int
    review_id: str
    approved_by: str
    approval_reason: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    environment: str
