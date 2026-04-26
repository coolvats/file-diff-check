"""
GitHub integration for approvals and notifications
"""

import logging
import requests
from typing import Optional, Dict
from datetime import datetime

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class GitHubIntegration:
    """Handle GitHub API interactions"""
    
    def __init__(self, token: str = settings.GITHUB_TOKEN):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_pr_comment(
        self,
        pr_number: int,
        comment: str,
        repo_owner: str = settings.GITHUB_OWNER,
        repo_name: str = settings.GITHUB_REPO
    ) -> bool:
        """
        Add a comment to a pull request
        
        Args:
            pr_number: Pull request number
            comment: Comment text
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
            data = {"body": comment}
            
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Comment added to PR #{pr_number}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding PR comment: {str(e)}")
            return False
    
    def create_check_run(
        self,
        commit_sha: str,
        name: str,
        status: str,
        conclusion: Optional[str] = None,
        details: Optional[Dict] = None,
        repo_owner: str = settings.GITHUB_OWNER,
        repo_name: str = settings.GITHUB_REPO
    ) -> bool:
        """
        Create a check run on a commit
        
        Args:
            commit_sha: Commit SHA
            name: Check run name
            status: Status (queued, in_progress, completed)
            conclusion: Conclusion (success, failure, neutral, cancelled, skipped, action_required)
            details: Additional details
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/check-runs"
            
            payload = {
                "name": name,
                "head_sha": commit_sha,
                "status": status,
                "started_at": datetime.now().isoformat() + "Z"
            }
            
            if status == "completed":
                payload["conclusion"] = conclusion or "success"
                payload["completed_at"] = datetime.now().isoformat() + "Z"
            
            if details:
                payload["output"] = {
                    "title": details.get("title", name),
                    "summary": details.get("summary", ""),
                    "text": details.get("text", "")
                }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Check run created for commit {commit_sha}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating check run: {str(e)}")
            return False
    
    def update_pr_status(
        self,
        pr_number: int,
        status: str,
        description: str,
        repo_owner: str = settings.GITHUB_OWNER,
        repo_name: str = settings.GITHUB_REPO
    ) -> bool:
        """
        Update PR status/review status
        
        Args:
            pr_number: Pull request number
            status: Status (approved, changes_requested, commented)
            description: Status description
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            True if successful
        """
        try:
            # Get PR info first
            pr_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=self.headers)
            pr_response.raise_for_status()
            
            pr_data = pr_response.json()
            commit_sha = pr_data["head"]["sha"]
            
            # Create status update
            status_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/statuses/{commit_sha}"
            
            status_payload = {
                "state": "success" if status == "approved" else "pending",
                "description": description,
                "context": "ci/cd/approval-workflow"
            }
            
            response = requests.post(status_url, json=status_payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"PR #{pr_number} status updated to {status}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating PR status: {str(e)}")
            return False
