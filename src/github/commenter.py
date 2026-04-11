from typing import Optional
from .client import GitHubClient

class CommentManager:
    """Manages the lifecycle of progress comments on GitHub."""

    def __init__(self, client: GitHubClient):
        self.client = client

    def upsert_progress_comment(self, repo_full_name: str, item_id: int, status: str, message: str, existing_comment_id: Optional[int] = None):
        """
        Creates or updates the live progress comment.
        """
        repo = self.client.get_repository(repo_full_name)
        issue = repo.get_issue(item_id)

        comment_body = f"### 🤖 Mythic Relay Progress\n**Status:** `{status}`\n\n{message}"

        if existing_comment_id:
            # Update existing comment
            comment = repo.get_issue_comment(existing_comment_id)
            comment.edit(body=comment_body)
            return comment.id
        else:
            # Create new comment
            comment = issue.create_comment(comment_body)
            return comment.id

    def add_reaction(self, repo_full_name: str, comment_id: int, reaction: str):
        """
        Adds a reaction (e.g., 'eyes', 'rocket', 'confused') to a comment.
        """
        repo = self.client.get_repository(repo_full_name)
        comment = repo.get_issue_comment(comment_id)
        comment.create_reaction(reaction)
