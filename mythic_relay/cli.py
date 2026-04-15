"""CLI commands for mythic_relay GitHub Actions workflow."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import TypedDict

__all__ = [
    "main",
    "parse_request",
    "build_prompt",
    "run_agent",
    "finalize_success",
    "finalize_failure",
]


@dataclass
class ParsedRequest:
    """Result of parsing an /ai request."""

    user_request: str
    model_override: str | None = None
    max_turns_override: int | None = None


class AgentResult(TypedDict):
    """Result of running the Claude agent."""

    result: str
    failure_reason: str
    agent_attempts: int


def parse_request(request_text: str) -> ParsedRequest:
    """Parse /ai request text into components.

    Supports formats:
      /ai <request>
      /ai --model <model> <request>
      /ai --max-turns <n> <request>
      /ai --model <model> --max-turns <n> <request>

    Args:
        request_text: The raw request text after /ai command.

    Returns:
        ParsedRequest with extracted components.
    """
    parts = request_text.strip().split()

    if not parts:
        return ParsedRequest(user_request="")

    model_override: str | None = None
    max_turns_override: int | None = None
    remaining: list[str] = []

    i = 0
    while i < len(parts):
        if parts[i] == "--model" and i + 1 < len(parts) and not parts[i + 1].startswith("--"):
            model_override = parts[i + 1]
            i += 2
        elif parts[i] == "--max-turns" and i + 1 < len(parts) and not parts[i + 1].startswith("--"):
            try:
                max_turns_override = int(parts[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            remaining.append(parts[i])
            i += 1

    return ParsedRequest(
        user_request=" ".join(remaining),
        model_override=model_override,
        max_turns_override=max_turns_override,
    )


def build_prompt(
    user_request: str,
    issue_title: str | None = None,
    issue_body: str | None = None,
    issue_number: int | None = None,
    repository: str | None = None,
) -> str:
    """Build the prompt for Claude agent.

    Args:
        user_request: The parsed user request text.
        issue_title: Optional issue title for context.
        issue_body: Optional issue body/description.
        issue_number: Optional issue number.
        repository: Optional repository full name (owner/repo).

    Returns:
        Complete prompt string for the Claude agent.
    """
    parts = []

    if repository:
        parts.append(f"Repository: {repository}")
    if issue_number:
        parts.append(f"Issue: #{issue_number}")

    if issue_title:
        parts.append("Task:")
        parts.append(f"Title: {issue_title}")
        if issue_body:
            parts.append(f"Description: {issue_body}")
    else:
        parts.append("Request:")
        if issue_body:
            parts.append(f"Description: {issue_body}")

    parts.append(f"User Request: {user_request}")

    prompt = "\n\n".join(parts)

    prompt += """

--- END ISSUE CONTENT ---

Work autonomously to implement the requested changes:
- Make necessary code changes
- Run relevant lint/tests when feasible
- Commit and push changes to the relay branch
- Create a PR if appropriate

Use the repository's existing patterns and follow best practices."""

    return prompt


def run_agent(
    prompt: str,
    model: str | None = None,
    max_turns: int | None = None,
    timeout: int = 600,
) -> AgentResult:
    """Run the Claude agent with the given prompt.

    Args:
        prompt: The prompt to send to Claude.
        model: Optional model override.
        max_turns: Optional max turns override.
        timeout: Timeout in seconds (default 600).

    Returns:
        Dict with 'result', 'failure_reason', and 'agent_attempts' keys.
        agent_attempts is always 1 (no retry logic implemented).
    """
    import subprocess

    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions"]

    if model:
        cmd.extend(["--model", model])
    if max_turns:
        cmd.extend(["--max-turns", str(max_turns)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            return {
                "result": "success",
                "failure_reason": "",
                "agent_attempts": 1,
            }
        else:
            failure_reason = _classify_failure(result.stderr, result.returncode)

            return {
                "result": "failure",
                "failure_reason": failure_reason,
                "agent_attempts": 1,
            }

    except subprocess.TimeoutExpired:
        return {
            "result": "failure",
            "failure_reason": "agent_timeout",
            "agent_attempts": 1,
        }
    except FileNotFoundError:
        return {
            "result": "failure",
            "failure_reason": "agent_error",
            "agent_attempts": 1,
        }
    except subprocess.SubprocessError:
        return {
            "result": "failure",
            "failure_reason": "agent_error",
            "agent_attempts": 1,
        }


def _classify_failure(stderr: str, returncode: int) -> str:
    """Classify agent failure from stderr content and return code.

    Args:
        stderr: The stderr output from the subprocess.
        returncode: The process return code.

    Returns:
        Failure reason string.
    """
    if returncode == 124:
        return "agent_timeout"

    if returncode == 126:
        return "auth_error"

    if returncode in (1, 2):
        stderr_lower = stderr.lower() if stderr else ""
        if "not authenticated" in stderr_lower or "permission denied" in stderr_lower:
            return "auth_error"
        if "timeout" in stderr_lower and ("exceeded" in stderr_lower or "limit" in stderr_lower):
            return "agent_timeout"

    return "agent_error"


def _write_output(key: str, value: str) -> None:
    """Write a key-value pair to $GITHUB_OUTPUT, handling multi-line values safely.

    Falls back to stdout print when GITHUB_OUTPUT env var is not set.

    Args:
        key: The output variable name.
        value: The output value.
    """
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        print(f"{key}={value} >> $GITHUB_OUTPUT")
        return

    if "\n" in value:
        with open(github_output, "a") as f:
            f.write(f"{key}<<EOF\n{value}\nEOF\n")
    else:
        with open(github_output, "a") as f:
            f.write(f"{key}={value}\n")


def finalize_success(pr_url: str | None = None, summary: str | None = None) -> None:
    """Output success finalization in GitHub Actions format.

    Args:
        pr_url: Optional PR URL created.
        summary: Optional summary of actions taken.
    """
    _write_output("status", "completed")
    _write_output("failure_reason", "")
    if pr_url:
        _write_output("pr_url", pr_url)
    if summary:
        _write_output("summary", summary)


def finalize_failure(failure_reason: str, summary: str | None = None) -> None:
    """Output failure finalization in GitHub Actions format.

    Args:
        failure_reason: The failure reason code.
        summary: Optional summary of what went wrong.
    """
    _write_output("status", "failed")
    _write_output("failure_reason", failure_reason)
    if summary:
        _write_output("summary", summary)


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a parser."""
    parser.add_argument("--issue-title", type=str, help="Issue title")
    parser.add_argument("--issue-body", type=str, help="Issue body")
    parser.add_argument("--issue-number", type=int, help="Issue number")
    parser.add_argument("--repository", type=str, help="Repository full name (owner/repo)")


def _main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(prog="mythic-relay")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # parse-request command
    parse_parser = subparsers.add_parser("parse-request", help="Parse /ai request text")
    parse_parser.add_argument("request_text", type=str, help="The request text to parse")
    _add_common_args(parse_parser)

    # build-prompt command
    prompt_parser = subparsers.add_parser("build-prompt", help="Build agent prompt")
    prompt_parser.add_argument("user_request", type=str, help="The user request text")
    _add_common_args(prompt_parser)

    # run-agent command
    agent_parser = subparsers.add_parser("run-agent", help="Run Claude agent")
    agent_parser.add_argument("prompt", type=str, help="The prompt for Claude")
    agent_parser.add_argument("--model", type=str, help="Model override")
    agent_parser.add_argument("--max-turns", type=int, help="Max turns override")
    agent_parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")

    # finalize-success command
    success_parser = subparsers.add_parser("finalize-success", help="Finalize with success")
    success_parser.add_argument("--pr-url", type=str, help="PR URL")
    success_parser.add_argument("--summary", type=str, help="Summary of actions")

    # finalize-failure command
    failure_parser = subparsers.add_parser("finalize-failure", help="Finalize with failure")
    failure_parser.add_argument("failure_reason", type=str, help="Failure reason")
    failure_parser.add_argument("--summary", type=str, help="Summary of failure")

    args = parser.parse_args()

    if args.command == "parse-request":
        result = parse_request(args.request_text)
        _write_output("user_request", result.user_request)
        _write_output("model_override", result.model_override or "")
        _write_output(
            "max_turns_override",
            str(result.max_turns_override) if result.max_turns_override is not None else "",
        )

    elif args.command == "build-prompt":
        prompt = build_prompt(
            user_request=args.user_request,
            issue_title=args.issue_title,
            issue_body=args.issue_body,
            issue_number=args.issue_number,
            repository=args.repository,
        )
        _write_output("prompt", prompt)

    elif args.command == "run-agent":
        agent_result = run_agent(
            prompt=args.prompt,
            model=args.model,
            max_turns=args.max_turns,
            timeout=args.timeout,
        )
        _write_output("result", agent_result["result"])
        _write_output("failure_reason", agent_result["failure_reason"])
        if agent_result["result"] == "failure":
            sys.exit(1)

    elif args.command == "finalize-success":
        finalize_success(pr_url=args.pr_url, summary=args.summary)

    elif args.command == "finalize-failure":
        finalize_failure(failure_reason=args.failure_reason, summary=args.summary)

    else:
        parser.print_help()
        sys.exit(1)


def main() -> None:
    """Entry point for console_scripts."""
    _main()


if __name__ == "__main__":
    _main()
