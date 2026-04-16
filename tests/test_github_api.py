"""Tests for mythic_relay.github.api module."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from mythic_relay.github.api import (
    DEFAULT_TIMEOUT,
    Comment,
    GitHubAPI,
    GitHubAPIError,
    Issue,
    PullRequest,
    Reaction,
    ReactionType,
)


class TestCommentFromResponse:
    """Tests for Comment.from_response factory."""

    def test_valid_response(self) -> None:
        """Test parsing a valid GitHub comment response."""
        data = {
            "id": 123,
            "body": "Test comment",
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        comment = Comment.from_response(data)
        assert comment.id == 123
        assert comment.body == "Test comment"
        assert comment.user == "octocat"
        assert comment.created_at == "2024-01-01T00:00:00Z"
        assert comment.updated_at == "2024-01-01T00:00:00Z"

    def test_missing_user_login(self) -> None:
        """Test that missing user.login raises GitHubAPIError."""
        data = {
            "id": 123,
            "body": "Test",
            "user": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing user.login"):
            Comment.from_response(data)

    def test_missing_user(self) -> None:
        """Test that missing user key raises GitHubAPIError."""
        data = {
            "id": 123,
            "body": "Test",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing user.login"):
            Comment.from_response(data)

    def test_missing_id_field(self) -> None:
        """Test that missing id field raises GitHubAPIError."""
        data = {
            "body": "Test",
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing 'id'"):
            Comment.from_response(data)

    def test_missing_body_field(self) -> None:
        """Test that missing body field raises GitHubAPIError."""
        data = {
            "id": 123,
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing 'body'"):
            Comment.from_response(data)


class TestReactionFromResponse:
    """Tests for Reaction.from_response factory."""

    def test_valid_response(self) -> None:
        """Test parsing a valid GitHub reaction response."""
        data = {
            "id": 456,
            "user": {"login": "octocat"},
            "content": "+1",
        }
        reaction = Reaction.from_response(data)
        assert reaction.id == 456
        assert reaction.user == "octocat"
        assert reaction.content == ReactionType.THUMBS_UP

    def test_heart_reaction(self) -> None:
        """Test parsing a heart reaction."""
        data = {"id": 789, "user": {"login": "octocat"}, "content": "heart"}
        reaction = Reaction.from_response(data)
        assert reaction.content == ReactionType.HEART

    def test_unknown_content(self) -> None:
        """Test that unknown reaction content raises GitHubAPIError."""
        data = {"id": 456, "user": {"login": "octocat"}, "content": "unknown_type"}
        with pytest.raises(GitHubAPIError, match="unknown content"):
            Reaction.from_response(data)

    def test_missing_user_login(self) -> None:
        """Test that missing user.login raises GitHubAPIError."""
        data = {"id": 456, "content": "+1"}
        with pytest.raises(GitHubAPIError, match="missing user.login"):
            Reaction.from_response(data)

    def test_missing_content_field(self) -> None:
        """Test that missing content field raises GitHubAPIError."""
        data = {"id": 456, "user": {"login": "octocat"}}
        with pytest.raises(GitHubAPIError, match="missing 'content'"):
            Reaction.from_response(data)


class TestPullRequestFromResponse:
    """Tests for PullRequest.from_response factory."""

    def test_valid_response(self) -> None:
        """Test parsing a valid GitHub PR response."""
        data = {
            "id": 1,
            "number": 42,
            "title": "Fix bug",
            "body": "Description",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/42",
            "draft": False,
            "user": {"login": "octocat"},
        }
        pr = PullRequest.from_response(data)
        assert pr.id == 1
        assert pr.number == 42
        assert pr.title == "Fix bug"
        assert pr.body == "Description"
        assert pr.state == "open"
        assert pr.html_url == "https://github.com/owner/repo/pull/42"
        assert pr.draft is False

    def test_draft_pr(self) -> None:
        """Test parsing a draft PR response."""
        data = {
            "id": 2,
            "number": 43,
            "title": "WIP",
            "body": "",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/43",
            "draft": True,
            "user": {"login": "octocat"},
        }
        pr = PullRequest.from_response(data)
        assert pr.draft is True

    def test_missing_user_login(self) -> None:
        """Test that missing user.login raises GitHubAPIError."""
        data = {
            "id": 1,
            "number": 42,
            "title": "Fix",
            "body": "",
            "state": "open",
            "html_url": "https://x.com",
            "draft": False,
        }
        with pytest.raises(GitHubAPIError, match="missing user.login"):
            PullRequest.from_response(data)

    def test_missing_number_field(self) -> None:
        """Test that missing number field raises GitHubAPIError."""
        data = {
            "id": 1,
            "title": "Fix",
            "body": "",
            "state": "open",
            "html_url": "https://x.com",
            "draft": False,
            "user": {"login": "octocat"},
        }
        with pytest.raises(GitHubAPIError, match="missing 'number'"):
            PullRequest.from_response(data)


class TestIssueFromResponse:
    """Tests for Issue.from_response factory."""

    def test_valid_response(self) -> None:
        """Test parsing a valid GitHub issue response."""
        data = {
            "id": 1,
            "number": 42,
            "title": "Bug report",
            "body": "Description",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/42",
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }
        issue = Issue.from_response(data)
        assert issue.id == 1
        assert issue.number == 42
        assert issue.title == "Bug report"
        assert issue.body == "Description"
        assert issue.state == "open"
        assert issue.html_url == "https://github.com/owner/repo/issues/42"
        assert issue.user == "octocat"
        assert issue.created_at == "2024-01-01T00:00:00Z"
        assert issue.updated_at == "2024-01-02T00:00:00Z"

    def test_closed_issue(self) -> None:
        """Test parsing a closed issue response."""
        data = {
            "id": 2,
            "number": 43,
            "title": "Fixed bug",
            "body": "Fixed",
            "state": "closed",
            "html_url": "https://github.com/owner/repo/issues/43",
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-03T00:00:00Z",
        }
        issue = Issue.from_response(data)
        assert issue.state == "closed"

    def test_missing_user_login(self) -> None:
        """Test that missing user.login raises GitHubAPIError."""
        data = {
            "id": 1,
            "number": 42,
            "title": "Bug",
            "body": "",
            "state": "open",
            "html_url": "https://x.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing user.login"):
            Issue.from_response(data)

    def test_missing_title_field(self) -> None:
        """Test that missing title field raises GitHubAPIError."""
        data = {
            "id": 1,
            "number": 42,
            "body": "Bug",
            "state": "open",
            "html_url": "https://x.com",
            "user": {"login": "octocat"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(GitHubAPIError, match="missing 'title'"):
            Issue.from_response(data)


class TestGitHubAPIRequest:
    """Tests for GitHubAPI._request method."""

    def test_get_request_success(self) -> None:
        """Test a successful GET request."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": 123}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            api = GitHubAPI("owner", "repo", token="test-token")
            result = api._request("GET", "/repos/owner/repo/issues/1")
            assert result == {"id": 123}
            mock_urlopen.assert_called_once()
            call_kwargs = mock_urlopen.call_args[1]
            assert call_kwargs["timeout"] == DEFAULT_TIMEOUT

    def test_delete_request_empty_body(self) -> None:
        """Test DELETE request with empty 204 response body."""
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo")
            result = api._request("DELETE", "/repos/owner/repo/issues/comments/123/reactions/456")
            assert result == {}

    def test_http_error_401(self) -> None:
        """Test HTTP 401 error raises GitHubAPIError with status code."""
        import io
        import urllib.error

        error = urllib.error.HTTPError(
            url="https://api.github.com/repos/owner/repo/issues/1",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"message": "Bad credentials"}'),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            api = GitHubAPI("owner", "repo")
            with pytest.raises(GitHubAPIError) as exc_info:
                api._request("GET", "/repos/owner/repo/issues/1")
            assert exc_info.value.status_code == 401
            assert "Bad credentials" in str(exc_info.value)

    def test_http_error_404(self) -> None:
        """Test HTTP 404 error raises GitHubAPIError."""
        import io
        import urllib.error

        error = urllib.error.HTTPError(
            url="https://api.github.com/repos/owner/repo/issues/999",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=io.BytesIO(b'{"message": "Not Found"}'),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            api = GitHubAPI("owner", "repo")
            with pytest.raises(GitHubAPIError) as exc_info:
                api._request("GET", "/repos/owner/repo/issues/999")
            assert exc_info.value.status_code == 404

    def test_http_error_429_rate_limit(self) -> None:
        """Test HTTP 429 rate limit error includes Retry-After header."""
        import io
        import urllib.error

        error = urllib.error.HTTPError(
            url="https://api.github.com/repos/owner/repo/issues/1",
            code=429,
            msg="Rate Limit Exceeded",
            hdrs={"Retry-After": "30"},
            fp=io.BytesIO(b'{"message": "Rate limit exceeded"}'),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            api = GitHubAPI("owner", "repo")
            with pytest.raises(GitHubAPIError) as exc_info:
                api._request("GET", "/repos/owner/repo/issues/1")
            assert exc_info.value.status_code == 429
            assert "30 seconds" in str(exc_info.value)

    def test_network_error(self) -> None:
        """Test network error raises GitHubAPIError."""
        import urllib.error

        with patch(
            "urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")
        ):
            api = GitHubAPI("owner", "repo")
            with pytest.raises(GitHubAPIError, match="Network error"):
                api._request("GET", "/repos/owner/repo/issues/1")

    def test_https_validation(self) -> None:
        """Test that non-HTTPS URLs raise GitHubAPIError."""
        api = GitHubAPI("owner", "repo")
        api._api_base = "http://api.github.com"
        with pytest.raises(GitHubAPIError, match="HTTPS"):
            api._request("GET", "/repos/owner/repo/issues/1")


class TestGitHubAPIAuth:
    """Tests for GitHubAPI authentication."""

    def test_token_from_constructor(self) -> None:
        """Test token passed via constructor is used."""
        api = GitHubAPI("owner", "repo", token="my-token")
        assert api._token == "my-token"

    def test_token_repr_redacted(self) -> None:
        """Test that __repr__ redacts the token."""
        api = GitHubAPI("owner", "repo", token="secret")
        repr_str = repr(api)
        assert "secret" not in repr_str
        assert "***" in repr_str

    def test_token_none_repr(self) -> None:
        """Test __repr__ when no token is set."""
        with patch.dict("os.environ", {}, clear=True):
            api = GitHubAPI("owner", "repo", token=None)
            repr_str = repr(api)
            assert "***" not in repr_str


class TestGitHubAPIIntegration:
    """Integration-style tests for GitHubAPI public methods using mocked network calls."""

    def test_create_comment(self) -> None:
        """Test creating a comment."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "id": 999,
                "body": "Nice fix!",
                "user": {"login": "reviewer"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            comment = api.create_comment(123, "Nice fix!")
            assert comment.id == 999
            assert comment.body == "Nice fix!"
            assert comment.user == "reviewer"

    def test_add_reaction(self) -> None:
        """Test adding a reaction to a comment."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "id": 777,
                "user": {"login": "reviewer"},
                "content": "+1",
            }
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            reaction = api.add_reaction(999, ReactionType.THUMBS_UP)
            assert reaction.id == 777
            assert reaction.content == ReactionType.THUMBS_UP

    def test_delete_reaction_success(self) -> None:
        """Test deleting a reaction returns without error on 204."""
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            # Should not raise
            api.delete_reaction(comment_id=999, reaction_id=777)

    def test_delete_reaction_unexpected_body(self) -> None:
        """Test delete_reaction raises error when response has unexpected body."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"error": "something went wrong"}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            with pytest.raises(GitHubAPIError, match="Unexpected response on delete"):
                api.delete_reaction(comment_id=999, reaction_id=777)

    def test_create_pull_request(self) -> None:
        """Test creating a pull request returns PullRequest dataclass."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "id": 1,
                "number": 42,
                "title": "New feature",
                "body": "Implements feature X",
                "state": "open",
                "html_url": "https://github.com/owner/repo/pull/42",
                "draft": True,
                "user": {"login": "developer"},
            }
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            pr = api.create_pull_request(
                title="New feature", body="Implements feature X", head="feature-branch"
            )
            assert isinstance(pr, PullRequest)
            assert pr.number == 42
            assert pr.title == "New feature"
            assert pr.draft is True

    def test_get_pull_request(self) -> None:
        """Test getting a pull request returns PullRequest dataclass."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "id": 1,
                "number": 42,
                "title": "Fix bug",
                "body": "Fixes issue #10",
                "state": "closed",
                "html_url": "https://github.com/owner/repo/pull/42",
                "draft": False,
                "user": {"login": "developer"},
            }
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            pr = api.get_pull_request(42)
            assert isinstance(pr, PullRequest)
            assert pr.state == "closed"

    def test_get_issue(self) -> None:
        """Test getting an issue returns Issue dataclass."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "id": 1,
                "number": 42,
                "title": "Bug report",
                "body": "Issue description",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/42",
                "user": {"login": "reporter"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            }
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            api = GitHubAPI("owner", "repo", token="tok")
            issue = api.get_issue(42)
            assert isinstance(issue, Issue)
            assert issue.number == 42
            assert issue.title == "Bug report"
            assert issue.user == "reporter"
