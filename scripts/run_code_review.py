"""
Script to run LangSmith code review
"""

import argparse
import json
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith_agent.code_review_agent import (
    LangSmithCodeReviewAgent,
    SecurityScanner,
    DependencyScanner
)
from app.models import CodeReviewRequest
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_scan_results(file_path):
    """Load scan results from JSON file"""
    try:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load {file_path}: {str(e)}")
    return {}


def main():
    parser = argparse.ArgumentParser(description="Run LangSmith code review")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")
    parser.add_argument("--branch-name", help="Branch name")
    parser.add_argument("--security-report", help="Path to security scan report")
    parser.add_argument("--dependency-report", help="Path to dependency scan report")
    
    args = parser.parse_args()
    
    try:
        # Get changed files
        import subprocess
        if args.commit_sha:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{args.commit_sha}~1..{args.commit_sha}"],
                capture_output=True,
                text=True
            )
            files_changed = result.stdout.strip().split('\n') if result.stdout else []
        else:
            files_changed = []
        
        # Load scan results
        security_results = load_scan_results(args.security_report) if args.security_report else {}
        dependency_results = load_scan_results(args.dependency_report) if args.dependency_report else {}
        
        # Create review request
        review_request = CodeReviewRequest(
            pr_number=args.pr_number,
            branch_name=args.branch_name,
            commit_sha=args.commit_sha,
            files_changed=files_changed,
            security_scan_results=security_results,
            dependency_scan_results=dependency_results
        )
        
        # Run code review
        agent = LangSmithCodeReviewAgent()
        review_response = agent.analyze_code_changes(review_request)
        
        # Save results
        with open("review-result.json", "w") as f:
            json.dump(review_response.model_dump(), f, indent=2, default=str)
        
        logger.info(f"Code review completed: {review_response.status}")
        
        # Exit with appropriate code
        if review_response.status == "approved":
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error in code review: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
