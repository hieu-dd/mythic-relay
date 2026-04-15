"""Tests for mythic_relay CLI commands."""

from mythic_relay.cli import (
    build_prompt,
    finalize_failure,
    finalize_success,
    parse_request,
    run_agent,
)


class TestParseRequest:
    """Tests for parse_request function."""

    def test_simple_request(self) -> None:
        """Test parsing a simple /ai request."""
        result = parse_request("Fix the login bug")
        assert result.user_request == "Fix the login bug"
        assert result.model_override is None
        assert result.max_turns_override is None

    def test_request_with_model(self) -> None:
        """Test parsing request with model override."""
        result = parse_request("--model opus Fix the login bug")
        assert result.user_request == "Fix the login bug"
        assert result.model_override == "opus"
        assert result.max_turns_override is None

    def test_request_with_max_turns(self) -> None:
        """Test parsing request with max turns override."""
        result = parse_request("--max-turns 10 Fix the login bug")
        assert result.user_request == "Fix the login bug"
        assert result.model_override is None
        assert result.max_turns_override == 10

    def test_request_with_both_overrides(self) -> None:
        """Test parsing request with both model and max turns."""
        result = parse_request("--model claude-3-opus --max-turns 5 Fix the login bug")
        assert result.user_request == "Fix the login bug"
        assert result.model_override == "claude-3-opus"
        assert result.max_turns_override == 5

    def test_empty_request(self) -> None:
        """Test parsing empty request."""
        result = parse_request("")
        assert result.user_request == ""
        assert result.model_override is None
        assert result.max_turns_override is None

    def test_request_with_leading_whitespace(self) -> None:
        """Test parsing request with leading whitespace."""
        result = parse_request("  Fix the login bug")
        assert result.user_request == "Fix the login bug"

    def test_request_model_followed_by_flag(self) -> None:
        """Test parsing request when --model is followed by another flag."""
        result = parse_request("--model --max-turns 5 Fix the login bug")
        assert result.user_request == "--model Fix the login bug"
        assert result.model_override is None
        assert result.max_turns_override == 5

    def test_request_max_turns_followed_by_flag(self) -> None:
        """Test parsing request when --max-turns is followed by another flag."""
        result = parse_request("--max-turns --model opus Fix the login bug")
        assert result.user_request == "--max-turns Fix the login bug"
        assert result.model_override == "opus"
        assert result.max_turns_override is None


class TestBuildPrompt:
    """Tests for build_prompt function."""

    def test_simple_prompt(self) -> None:
        """Test building prompt with just user request."""
        result = build_prompt("Fix the login bug")
        assert "Fix the login bug" in result
        assert "User Request: Fix the login bug" in result

    def test_prompt_with_issue_context(self) -> None:
        """Test building prompt with issue context."""
        result = build_prompt(
            user_request="Fix the bug",
            issue_title="Login broken",
            issue_number=123,
            repository="owner/repo",
        )
        assert "Repository: owner/repo" in result
        assert "Issue: #123" in result
        assert "Title: Login broken" in result
        assert "Fix the bug" in result

    def test_prompt_includes_instructions(self) -> None:
        """Test that prompt includes autonomous work instructions."""
        result = build_prompt("Fix the bug")
        assert "Work autonomously" in result
        assert "Commit and push" in result

    def test_prompt_with_body_only_separator(self) -> None:
        """Test that prompt adds blank line between sections when no title."""
        result = build_prompt("Fix the bug", issue_body="The bug is in login")
        assert "Request:\n\nDescription:" in result

    def test_prompt_with_all_sections(self) -> None:
        """Test that prompt sections are properly separated."""
        result = build_prompt(
            user_request="Fix it",
            issue_title="Title",
            issue_body="Body",
            issue_number=1,
            repository="owner/repo",
        )
        assert "\n\n" in result  # Blank line between sections


class TestRunAgent:
    """Tests for run_agent function."""

    def test_run_agent_returns_dict(self) -> None:
        """Test that run_agent returns expected dict structure."""
        result = run_agent("test prompt", timeout=1)
        assert "result" in result
        assert "failure_reason" in result

    def test_run_agent_nonexistent_command(self) -> None:
        """Test run_agent handles missing claude gracefully."""
        result = run_agent("test prompt", timeout=1)
        assert result["result"] == "failure"
        # Either agent_error (command not found) or agent_timeout (timed out) is valid
        assert result["failure_reason"] in ("agent_error", "agent_timeout")


class TestFinalizeFunctions:
    """Tests for finalize_success and finalize_failure functions."""

    def test_finalize_success_basic(self, capsys) -> None:
        """Test finalize_success basic output."""
        finalize_success()
        captured = capsys.readouterr()
        assert "status=completed >> $GITHUB_OUTPUT" in captured.out
        assert "failure_reason= >> $GITHUB_OUTPUT" in captured.out

    def test_finalize_success_with_pr_url(self, capsys) -> None:
        """Test finalize_success with PR URL."""
        finalize_success(pr_url="https://github.com/owner/repo/pull/123")
        captured = capsys.readouterr()
        assert "pr_url=https://github.com/owner/repo/pull/123 >> $GITHUB_OUTPUT" in captured.out

    def test_finalize_failure_basic(self, capsys) -> None:
        """Test finalize_failure basic output."""
        finalize_failure("agent_error")
        captured = capsys.readouterr()
        assert "status=failed >> $GITHUB_OUTPUT" in captured.out
        assert "failure_reason=agent_error >> $GITHUB_OUTPUT" in captured.out

    def test_finalize_failure_with_summary(self, capsys) -> None:
        """Test finalize_failure with summary."""
        finalize_failure("agent_timeout", summary="Agent timed out after 10 minutes")
        captured = capsys.readouterr()
        assert "summary=Agent timed out after 10 minutes >> $GITHUB_OUTPUT" in captured.out
