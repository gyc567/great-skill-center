#!/usr/bin/env python3
"""
GitHub Repo Info Fetcher
Fetches key information from a GitHub repository for evaluation.
"""

import sys
import json
import re
from datetime import datetime, timedelta
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


def extract_repo_info(url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    patterns = [
        r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'github\.com/([^/]+)/([^/]+?)(?:/.*)?$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
    raise ValueError(f"Invalid GitHub URL: {url}")


def fetch_readme(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """Fetch README content."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/readme",
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        import base64
        content = resp.json().get("content", "")
        # Content is base64 encoded
        try:
            decoded = base64.b64decode(content).decode("utf-8")
        except:
            decoded = content
        return {"found": True, "content": decoded[:2000]}  # Limit size
    return {"found": False, "content": ""}


def fetch_releases(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """Fetch release information."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        releases = resp.json()
        return {
            "found": True,
            "count": len(releases),
            "latest": releases[0]["tag_name"] if releases else None,
            "has_assets": bool(releases and releases[0].get("assets")),
        }
    return {"found": False, "count": 0, "latest": None, "has_assets": False}


def fetch_repo_stats(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """Fetch repository statistics."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        return {
            "found": True,
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "subscribers": data.get("subscribers_count", 0),
            "language": data.get("language"),
            "description": data.get("description"),
            "homepage": data.get("homepage"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "created_at": data.get("created_at"),
            "license": data.get("license", {}).get("name") if data.get("license") else None,
        }
    return {"found": False}


def fetch_recent_commits(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """Fetch recent commit activity."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=30",
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        commits = resp.json()
        if commits:
            latest_date = commits[0].get("commit", {}).get("author", {}).get("date", "")
            return {"found": True, "latest_commit": latest_date, "count": len(commits)}
    return {"found": False, "latest_commit": None, "count": 0}


def fetch_issues(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """Fetch recent issues (open)."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&sort=updated&per_page=20",
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        issues = resp.json()
        return {
            "found": True,
            "open_count": len(issues),
            "recent_titles": [i.get("title", "")[:80] for i in issues[:5]],
        }
    return {"found": False, "open_count": 0, "recent_titles": []}


def is_recently_updated(updated_at: Optional[str], months: int = 6) -> bool:
    """Check if repo was updated in last N months."""
    if not updated_at:
        return False
    try:
        from datetime import timezone
        # Handle ISO format with Z suffix
        clean_at = updated_at.replace("Z", "+00:00")
        # Parse the date
        updated = datetime.fromisoformat(clean_at)
        # Make threshold timezone-aware to match
        threshold = datetime.now(timezone.utc) - timedelta(days=months * 30)
        return updated > threshold
    except Exception:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_repo_info.py <github-url> [github-token]")
        sys.exit(1)

    url = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        owner, repo = extract_repo_info(url)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    result = {
        "owner": owner,
        "repo": repo,
        "timestamp": datetime.now().isoformat(),
    }

    # Fetch all info
    result["readme"] = fetch_readme(owner, repo, token)
    result["releases"] = fetch_releases(owner, repo, token)
    result["stats"] = fetch_repo_stats(owner, repo, token)
    result["commits"] = fetch_recent_commits(owner, repo, token)
    result["issues"] = fetch_issues(owner, repo, token)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
