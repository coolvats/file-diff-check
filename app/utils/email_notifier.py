"""Email utility functions for sending approval requests"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications"""
    
    def __init__(
        self,
        smtp_server: str = settings.SMTP_SERVER,
        smtp_port: int = settings.SMTP_PORT,
        username: str = settings.SMTP_USERNAME,
        password: str = settings.SMTP_PASSWORD
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_approval_request(
        self,
        recipient: str,
        pr_number: int,
        review_id: str,
        security_issues: list,
        dependency_issues: list,
        approval_url: str
    ) -> bool:
        """
        Send approval request email
        
        Args:
            recipient: Email recipient
            pr_number: Pull request number
            review_id: Code review ID
            security_issues: List of security issues found
            dependency_issues: List of dependency issues found
            approval_url: URL for approval action
        
        Returns:
            True if email sent successfully
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = f"[ACTION REQUIRED] Code Review Approval Needed - PR #{pr_number}"
            message["From"] = self.username
            message["To"] = recipient
            
            # Create plain text version
            text_content = f"""
Code Review Approval Request

PR Number: {pr_number}
Review ID: {review_id}

Security Issues Found: {len(security_issues)}
{self._format_list(security_issues)}

Dependency Issues Found: {len(dependency_issues)}
{self._format_list(dependency_issues)}

Action Required:
Please review the code changes and approve or reject the deployment.

Approval Link: {approval_url}

This is an automated message from File Duplicate Checker CI/CD Pipeline.
            """
            
            # Create HTML version
            html_content = f"""
            <html>
              <body>
                <h2>Code Review Approval Request</h2>
                <p><strong>PR Number:</strong> {pr_number}</p>
                <p><strong>Review ID:</strong> {review_id}</p>
                
                <h3>Security Issues Found: {len(security_issues)}</h3>
                <ul>
                    {self._format_html_list(security_issues)}
                </ul>
                
                <h3>Dependency Issues Found: {len(dependency_issues)}</h3>
                <ul>
                    {self._format_html_list(dependency_issues)}
                </ul>
                
                <p><strong>Action Required:</strong></p>
                <p>Please review the code changes and approve or reject the deployment.</p>
                
                <p><a href="{approval_url}">Click here to review and approve</a></p>
                
                <hr>
                <p><em>This is an automated message from File Duplicate Checker CI/CD Pipeline.</em></p>
              </body>
            </html>
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            logger.info(f"Approval request email sent to {recipient} for PR #{pr_number}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending approval email: {str(e)}")
            return False
    
    @staticmethod
    def _format_list(items: list) -> str:
        """Format list items as text"""
        if not items:
            return "None"
        return "\n".join([f"  - {item}" for item in items])
    
    @staticmethod
    def _format_html_list(items: list) -> str:
        """Format list items as HTML"""
        if not items:
            return "<li>None</li>"
        return "".join([f"<li>{item}</li>" for item in items])
