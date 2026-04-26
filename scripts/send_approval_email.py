"""
Script to send approval request emails
"""

import argparse
import json
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.email_notifier import EmailNotifier
from app.config import settings
from app.utils.logger import setup_logger
from langsmith_agent.code_review_agent import LangSmithCodeReviewAgent

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Send approval request email")
    parser.add_argument("--pr-number", type=int, required=True, help="Pull request number")
    parser.add_argument("--commit-sha", required=True, help="Commit SHA")
    parser.add_argument("--review-file", help="Path to review result JSON")
    
    args = parser.parse_args()
    
    try:
        # Load review results if available
        security_issues = []
        dependency_issues = []
        review_id = f"review_{args.commit_sha[:8]}"
        
        if args.review_file and Path(args.review_file).exists():
            with open(args.review_file, 'r') as f:
                review_data = json.load(f)
                security_issues = review_data.get("security_issues", [])
                dependency_issues = review_data.get("dependency_issues", [])
                review_id = review_data.get("review_id", review_id)
        
        # Generate approval URL
        agent = LangSmithCodeReviewAgent()
        approval_url = agent.generate_approval_url(review_id, args.pr_number)
        
        # Send email
        notifier = EmailNotifier()
        if notifier.send_approval_request(
            recipient=settings.APPROVAL_EMAIL,
            pr_number=args.pr_number,
            review_id=review_id,
            security_issues=security_issues,
            dependency_issues=dependency_issues,
            approval_url=approval_url
        ):
            logger.info(f"Approval email sent to {settings.APPROVAL_EMAIL}")
            sys.exit(0)
        else:
            logger.error("Failed to send approval email")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error sending approval email: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
