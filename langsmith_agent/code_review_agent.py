"""
LangSmith Fleet Agent for Code Review and Approval
Integrates with LangChain and LangSmith for intelligent code analysis
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
import json

from app.config import settings
from app.models import CodeReviewRequest, CodeReviewResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LangSmithCodeReviewAgent:
    """
    Fleet agent powered by LangSmith for code review and approval workflow
    """
    
    def __init__(
        self,
        api_key: str = settings.LANGSMITH_API_KEY,
        endpoint: str = settings.LANGSMITH_ENDPOINT,
        project: str = settings.LANGSMITH_PROJECT
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.project = project
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_code_changes(self, review_request: CodeReviewRequest) -> CodeReviewResponse:
        """
        Analyze code changes using LangSmith fleet agent
        
        Args:
            review_request: Code review request with file changes and scan results
        
        Returns:
            CodeReviewResponse with analysis and recommendations
        """
        try:
            logger.info(f"Starting code analysis for commit {review_request.commit_sha}")
            
            # Prepare analysis context
            context = self._prepare_analysis_context(review_request)
            
            # Call LangSmith API for analysis
            response = self._call_langsmith_api(context)
            
            # Parse response and generate review
            review_response = self._parse_langsmith_response(response, review_request)
            
            logger.info(f"Code analysis completed for commit {review_request.commit_sha}")
            return review_response
        
        except Exception as e:
            logger.error(f"Error in code analysis: {str(e)}")
            raise
    
    def _prepare_analysis_context(self, review_request: CodeReviewRequest) -> Dict:
        """Prepare context for LangSmith analysis"""
        return {
            "commit_sha": review_request.commit_sha,
            "branch_name": review_request.branch_name,
            "pr_number": review_request.pr_number,
            "files_changed": review_request.files_changed,
            "security_scan_results": review_request.security_scan_results or {},
            "dependency_scan_results": review_request.dependency_scan_results or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def _call_langsmith_api(self, context: Dict) -> Dict:
        """
        Call LangSmith API for code analysis
        
        For demonstration, this uses a simplified mock response.
        In production, this would call the actual LangSmith API.
        """
        try:
            # In production, uncomment to call actual LangSmith API:
            # url = f"{self.endpoint}/projects/{self.project}/analyze"
            # response = requests.post(url, json=context, headers=self.headers)
            # return response.json()
            
            # Mock response for demonstration
            logger.info("Using mock LangSmith response for demonstration")
            return self._generate_mock_analysis(context)
        
        except Exception as e:
            logger.error(f"Error calling LangSmith API: {str(e)}")
            raise
    
    def _generate_mock_analysis(self, context: Dict) -> Dict:
        """Generate mock analysis response"""
        return {
            "analysis_id": f"analysis_{context['commit_sha'][:8]}",
            "status": "completed",
            "recommendations": [
                "Code follows established patterns",
                "All files have proper error handling",
                "Documentation is comprehensive"
            ],
            "security_issues": context.get("security_scan_results", {}).get("vulnerabilities", []),
            "dependency_issues": context.get("dependency_scan_results", {}).get("issues", []),
            "approval_needed": len(context.get("security_scan_results", {}).get("vulnerabilities", [])) > 0
        }
    
    def _parse_langsmith_response(
        self,
        response: Dict,
        review_request: CodeReviewRequest
    ) -> CodeReviewResponse:
        """Parse LangSmith response into CodeReviewResponse"""
        
        security_issues = response.get("security_issues", [])
        dependency_issues = response.get("dependency_issues", [])
        
        # Determine approval status
        if security_issues or dependency_issues:
            status = "needs_changes"
        else:
            status = "approved"
        
        approval_required = len(security_issues) > 0 or len(dependency_issues) > 0
        
        return CodeReviewResponse(
            review_id=response.get("analysis_id", f"review_{review_request.commit_sha[:8]}"),
            status=status,
            recommendations=response.get("recommendations", []),
            security_issues=security_issues,
            dependency_issues=dependency_issues,
            approval_required=approval_required
        )
    
    def generate_approval_url(self, review_id: str, pr_number: int) -> str:
        """
        Generate approval URL for deployment
        
        Args:
            review_id: Code review ID
            pr_number: Pull request number
        
        Returns:
            Approval URL
        """
        base_url = f"{settings.GITHUB_REPO}/pull/{pr_number}"
        approval_params = f"?review_id={review_id}&action=approve"
        return f"{base_url}{approval_params}"


class SecurityScanner:
    """Security scanning with Bandit"""
    
    @staticmethod
    def scan_files(file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Scan files for security issues using Bandit
        
        Args:
            file_paths: List of Python files to scan
        
        Returns:
            Dictionary with vulnerabilities found
        """
        try:
            import subprocess
            
            vulnerabilities = []
            
            for file_path in file_paths:
                if file_path.endswith(".py"):
                    try:
                        result = subprocess.run(
                            ["bandit", "-f", "json", file_path],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.stdout:
                            output = json.loads(result.stdout)
                            for issue in output.get("results", []):
                                vulnerabilities.append({
                                    "file": file_path,
                                    "issue": issue.get("issue_text"),
                                    "severity": issue.get("severity"),
                                    "line": issue.get("line_number")
                                })
                    except Exception as e:
                        logger.warning(f"Error scanning {file_path}: {str(e)}")
            
            return {"vulnerabilities": vulnerabilities}
        
        except ImportError:
            logger.warning("Bandit not installed, skipping security scan")
            return {"vulnerabilities": []}


class DependencyScanner:
    """Dependency scanning for security vulnerabilities"""
    
    @staticmethod
    def scan_dependencies() -> Dict[str, List[str]]:
        """
        Scan dependencies for vulnerabilities using Safety
        
        Returns:
            Dictionary with dependency issues found
        """
        try:
            import subprocess
            
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                return {"issues": issues}
            
            return {"issues": []}
        
        except Exception as e:
            logger.warning(f"Error scanning dependencies: {str(e)}")
            return {"issues": []}
