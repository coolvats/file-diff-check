import argparse
import json
import os
from typing import Dict, Any

from github import Github
from langsmith import Client
from langchain.chat_models import ChatOpenAI


# -----------------------------
# Argument Parsing
# -----------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="PR Code Review with LangSmith Fleet integration")

    parser.add_argument("--repo", required=False, help="GitHub repo in org/name format")
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--branch-name", required=True)

    parser.add_argument("--security-report", required=True)
    parser.add_argument("--dependency-report", required=True)
    parser.add_argument("--pr-commit-summary", required=False)

    return parser.parse_args()


# -----------------------------
# Load JSON Helper
# -----------------------------
def load_json(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# Fetch PR Details (Metadata)
# -----------------------------
def fetch_pr_metadata(repo_name: str, pr_number: int) -> Dict[str, Any]:
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    return {
        "title": pr.title,
        "author": pr.user.login,
        "changed_files": pr.changed_files,
        "additions": pr.additions,
        "deletions": pr.deletions,
        "base_branch": pr.base.ref,
    }


# -----------------------------
# Fleet Agent Invocation
# -----------------------------
def run_fleet_commit_agent(repo: str, pr_number: int) -> Dict[str, Any]:
    """
    Calls LangSmith Fleet Agent that summarizes PR commit history
    """
    client = Client()

    result = client.run(
        "pr_commit_history_agent",
        inputs={
            "repo": repo,
            "pr_number": pr_number
        }
    )

    return result


# -----------------------------
# Core Review Logic
# -----------------------------
def run_review(args):
    repo = args.repo or os.environ.get("GITHUB_REPOSITORY")

    # Load reports
    security_report = load_json(args.security_report)
    dependency_report = load_json(args.dependency_report)

    # PR metadata
    pr_metadata = fetch_pr_metadata(repo, args.pr_number)

    # PR commit summary (Fleet)
    if args.pr_commit_summary and os.path.exists(args.pr_commit_summary):
        pr_commit_summary = load_json(args.pr_commit_summary)
    else:
        pr_commit_summary = run_fleet_commit_agent(repo, args.pr_number)

    # -----------------------------
    # LLM‑assisted synthesis
    # -----------------------------
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    prompt = f"""
You are a senior PR review assistant.

Inputs:
- PR metadata
- Commit history summary (from Fleet Agent)
- Security scan results
- Dependency scan results

Your task:
- Summarise risks
- Identify review focus areas
- Recommend whether approval is required

Rules:
- Do NOT approve or reject code
- Do NOT rewrite code
- Base conclusions strictly on provided inputs
- Keep output concise and structured
"""

    response = llm.invoke(
        prompt + "\n\n" +
        json.dumps({
            "pr_metadata": pr_metadata,
            "commit_summary": pr_commit_summary,
            "security_report": security_report,
            "dependency_report": dependency_report
        }, indent=2)
    )

    # -----------------------------
    # Final Review Output
    # -----------------------------
    review_result = {
        "status": "REVIEW_REQUIRED",
        "approval_required": True,
        "pr_title": pr_metadata["title"],
        "commit_count": pr_commit_summary.get("commit_count"),
        "main_changes": pr_commit_summary.get("summary", {}).get("main_changes", []),
        "risk_flags": pr_commit_summary.get("summary", {}).get("risk_flags", []),
        "security_issues": security_report.get("results", []),
        "dependency_issues": dependency_report.get("dependencies", []),
        "recommendations": response.content if hasattr(response, "content") else str(response)
    }

    with open("review-result.json", "w") as f:
        json.dump(review_result, f, indent=2)

    print("✅ Review completed. Output written to review-result.json")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    args = parse_args()
    run_review(args)
``
