import argparse
import json
import os
from typing import List, Dict

from github import Github
from langsmith import Client


# -------------------------------------------------
# Argument parsing
# -------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch PR commit history and send to LangSmith Fleet agent"
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in org/repo format"
    )
    parser.add_argument(
        "--pr-number",
        required=True,
        type=int,
        help="Pull request number"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )

    return parser.parse_args()


# -------------------------------------------------
# Fetch PR commits from GitHub
# -------------------------------------------------
def fetch_pr_commits(repo_name: str, pr_number: int) -> List[Dict]:
    """
    Fetch commit history for a PR using GitHub API
    """
    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    commits_data = []
    for commit in pr.get_commits():
        commits_data.append({
            "sha": commit.sha,
            "author": commit.commit.author.name if commit.commit.author else None,
            "message": commit.commit.message,
            "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
            "url": commit.html_url
        })

    return commits_data


# -------------------------------------------------
# Invoke LangSmith Fleet agent
# -------------------------------------------------
def run_fleet_agent(
    repo: str,
    pr_number: int,
    commits: List[Dict]
) -> Dict:
    """
    Sends commit history to LangSmith Fleet PR Commit History Agent
    """
    client = Client()

    result = client.run(
        "pr_commit_history_agent",  # ✅ Fleet agent name
        inputs={
            "repository": repo,
            "pr_number": pr_number,
            "commits": commits
        }
    )

    return result


# -------------------------------------------------
# Main execution
# -------------------------------------------------
def main():
    args = parse_args()

    print("🔍 Fetching PR commit history from GitHub...")
    commits = fetch_pr_commits(
        repo_name=args.repo,
        pr_number=args.pr_number
    )

    print(f"✅ Retrieved {len(commits)} commits")

    print("🚀 Sending commit history to LangSmith Fleet agent...")
    fleet_result = run_fleet_agent(
        repo=args.repo,
        pr_number=args.pr_number,
        commits=commits
    )

    output_payload = {
        "repository": args.repo,
        "pr_number": args.pr_number,
        "commit_count": len(commits),
        "commits": commits,
        "fleet_summary": fleet_result
    }

    with open(args.output, "w") as f:
        json.dump(output_payload, f, indent=2)

    print(f"📄 Fleet commit summary written to {args.output}")


if __name__ == "__main__":
    main()
``
