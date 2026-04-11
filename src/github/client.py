import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubClient:
    """Wrapper for PyGitHub with authentication and rate-limit handling."""

    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
        self.client = Github(token)

    def get_repository(self, repo_full_name: str):
        return self.client.get_repo(repo_full_name)

    def get_issue(self, repo_full_name: str, issue_number: int):
        repo = self.get_repository(repo_full_name)
        return repo.get_issue(issue_number)
