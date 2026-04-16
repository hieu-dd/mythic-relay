"""GitHub API wrapper for comments, reactions, and PR operations."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Any

DEFAULT_TIMEOUT = 30


class ReactionType(str, Enum):
    """Available reaction types for GitHub comments."""

    THUMBS_UP = "+1"
    THUMBS_DOWN = "-1"
    LAUGH = "laugh"
    CONFUSED = "confused"
    HEART = "heart"
    HOORAY = "hooray"
    ROCKET = "rocket"
    EYES = "eyes"


class GitHubAPIError(Exception):
    """Exception raised when GitHub API calls fail."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class Comment:
    """Represents a GitHub issue or PR comment."""

    id: int
    body: str
    user: str
    created_at: str
    updated_at: str

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Comment:
        """Create a Comment from a GitHub API response dict."""
        user = data.get("user")
        if not user or "login" not in user:
            raise GitHubAPIError(f"Invalid comment response: missing user.login in {data!r}")
        for field in ("id", "body", "created_at", "updated_at"):
            if field not in data:
                raise GitHubAPIError(f"Invalid comment response: missing '{field}' in {data!r}")
        return cls(
            id=data["id"],
            body=data["body"],
            user=user["login"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


@dataclass
class Reaction:
    """Represents a GitHub reaction to a comment."""

    id: int
    user: str
    content: ReactionType

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Reaction:
        """Create a Reaction from a GitHub API response dict."""
        user = data.get("user")
        if not user or "login" not in user:
            raise GitHubAPIError(f"Invalid reaction response: missing user.login in {data!r}")
        for field in ("id", "content"):
            if field not in data:
                raise GitHubAPIError(f"Invalid reaction response: missing '{field}' in {data!r}")
        try:
            content = ReactionType(data["content"])
        except ValueError:
            raise GitHubAPIError(
                f"Invalid reaction response: unknown content {data['content']!r} in {data!r}"
            )
        return cls(
            id=data["id"],
            user=user["login"],
            content=content,
        )


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""

    id: int
    number: int
    title: str
    body: str
    state: str
    html_url: str
    draft: bool

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> PullRequest:
        """Create a PullRequest from a GitHub API response dict."""
        user = data.get("user")
        if not user or "login" not in user:
            raise GitHubAPIError(f"Invalid pull request response: missing user.login in {data!r}")
        for field in ("id", "number", "title", "body", "state", "html_url", "draft"):
            if field not in data:
                raise GitHubAPIError(
                    f"Invalid pull request response: missing '{field}' in {data!r}"
                )
        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data["body"],
            state=data["state"],
            html_url=data["html_url"],
            draft=data["draft"],
        )


class GitHubAPI:
    """GitHub API wrapper for issue/PR operations."""

    def __init__(self, owner: str, repo: str, token: str | None = None) -> None:
        """Initialize the GitHub API wrapper.

        Args:
            owner: Repository owner (user or org).
            repo: Repository name.
            token: GitHub personal access token. Defaults to GITHUB_TOKEN env var.

        Note:
            The token is stored for API authentication and is redacted in __repr__.
            Do not log GitHubAPI instances directly.
        """
        self.owner = owner
        self.repo = repo
        self._token = (
            token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT") or None
        )
        self._api_base = "https://api.github.com"

    def __repr__(self) -> str:
        """Return a redacted representation of the GitHubAPI instance."""
        return (
            f"GitHubAPI(owner={self.owner!r}, repo={self.repo!r}, "
            f"token={'***' if self._token else None!r})"
        )

    def _headers(self) -> dict[str, str]:
        """Return headers for GitHub API requests."""
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            path: API path (e.g., /repos/owner/repo/issues/123/comments).
            data: Optional JSON body data.

        Returns:
            Parsed JSON response dict.

        Raises:
            GitHubAPIError: If the request fails.
        """
        url = f"{self._api_base}{path}"
        if not url.startswith("https://"):
            raise GitHubAPIError("GitHub API only supports HTTPS.")
        headers = self._headers()

        body: bytes | None = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
                content = response.read()
                if not content:
                    return {}
                return json.loads(content.decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            if e.code == 429:
                retry_after = e.headers.get("Retry-After", "unknown")
                raise GitHubAPIError(
                    f"GitHub API rate limit exceeded. Retry after {retry_after} seconds.",
                    status_code=429,
                ) from e
            try:
                error_json = json.loads(error_body)
                message = error_json.get("message", str(e))
            except json.JSONDecodeError:
                message = f"HTTP {e.code}: {error_body or str(e)}"
            raise GitHubAPIError(message, status_code=e.code) from e
        except urllib.error.URLError as e:
            raise GitHubAPIError(f"Network error: {e.reason}") from e

    def create_comment(self, issue_number: int, body: str) -> Comment:
        """Create a comment on an issue or pull request.

        Args:
            issue_number: The issue or PR number.
            body: The comment body text.

        Returns:
            Comment object representing the created comment.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        response = self._request("POST", path, {"body": body})
        return Comment.from_response(response)

    def update_comment(self, comment_id: int, body: str) -> Comment:
        """Update an existing comment.

        Args:
            comment_id: The comment ID.
            body: The new comment body text.

        Returns:
            Comment object representing the updated comment.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/issues/comments/{comment_id}"
        response = self._request("PATCH", path, {"body": body})
        return Comment.from_response(response)

    def get_comment(self, comment_id: int) -> Comment:
        """Get a single comment by ID.

        Args:
            comment_id: The comment ID.

        Returns:
            Comment object representing the comment.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/issues/comments/{comment_id}"
        response = self._request("GET", path)
        return Comment.from_response(response)

    def add_reaction(self, comment_id: int, reaction: ReactionType) -> Reaction:
        """Add a reaction to a comment.

        Args:
            comment_id: The comment ID.
            reaction: The reaction type to add.

        Returns:
            Reaction object representing the added reaction.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/issues/comments/{comment_id}/reactions"
        reaction_data = self._request("POST", path, {"content": reaction.value})
        return Reaction.from_response(reaction_data)

    def delete_reaction(self, comment_id: int, reaction_id: int) -> None:
        """Delete a reaction from a comment.

        Args:
            comment_id: The comment ID.
            reaction_id: The reaction ID to delete.

        Raises:
            GitHubAPIError: If the API call fails or returns an unexpected response.
        """
        path = (
            f"/repos/{self.owner}/{self.repo}/issues/comments/{comment_id}/reactions/{reaction_id}"
        )
        # DELETE returns 204 No Content with empty body; any non-empty body is unexpected.
        response = self._request("DELETE", path)
        if response:
            raise GitHubAPIError(f"Unexpected response on delete: {response}")

    def get_issue(self, issue_number: int) -> dict[str, Any]:
        """Get an issue or pull request details.

        Args:
            issue_number: The issue or PR number.

        Returns:
            Issue/PR data dict from GitHub API.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        return self._request("GET", path)

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = True,
    ) -> PullRequest:
        """Create a pull request.

        Args:
            title: PR title.
            body: PR body/description.
            head: Branch head (source branch).
            base: Base branch to merge into. Defaults to 'main'.
            draft: Whether to create as draft PR. Defaults to True.

        Returns:
            PullRequest object representing the created PR.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/pulls"
        return PullRequest.from_response(
            self._request(
                "POST",
                path,
                {
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base,
                    "draft": draft,
                },
            )
        )

    def get_pull_request(self, pr_number: int) -> PullRequest:
        """Get a pull request details.

        Args:
            pr_number: The PR number.

        Returns:
            PullRequest object representing the PR.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        path = f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
        return PullRequest.from_response(self._request("GET", path))
