"""CLI commands for mythic_relay GitHub Actions workflow."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import TypedDict

__all__ = ["main", "parse_request", "build_prompt", "run_agent", "finalize_success", "finalize_failure"]


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

    parts.append("Task:" if issue_title else "Request:")

    if issue_title:
        parts.append(f"Title: {issue_title}")
    if issue_body:
        parts.append(f"Description: {issue_body}")

    parts.append(f"User Request: {user_request}")

    prompt = "\n\n".join(parts)

    prompt += """

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
            }
        else:
            stderr = result.stderr.lower() if result.stderr else ""
            if "auth" in stderr or "permission" in stderr:
                failure_reason = "auth_error"
            elif "timeout" in stderr:
                failure_reason = "agent_timeout"
            else:
                failure_reason = "agent_error"

            return {
                "result": "failure",
                "failure_reason": failure_reason,
            }

    except subprocess.TimeoutExpired:
        return {
            "result": "failure",
            "failure_reason": "agent_timeout",
        }
    except FileNotFoundError:
        return {
            "result": "failure",
            "failure_reason": "agent_error",
        }
    except Exception:
        return {
            "result": "failure",
            "failure_reason": "agent_error",
        }


def finalize_success(pr_url: str | None = None, summary: str | None = None) -> None:
    """Output success finalization in GitHub Actions format.

    Args:
        pr_url: Optional PR URL created.
        summary: Optional summary of actions taken.
    """
    print("status=completed >> $GITHUB_OUTPUT")
    print("failure_reason= >> $GITHUB_OUTPUT")
    if pr_url:
        print(f"pr_url={pr_url} >> $GITHUB_OUTPUT")
    if summary:
        print(f"summary={summary} >> $GITHUB_OUTPUT")


def finalize_failure(failure_reason: str, summary: str | None = None) -> None:
    """Output failure finalization in GitHub Actions format.

    Args:
        failure_reason: The failure reason code.
        summary: Optional summary of what went wrong.
    """
    print("status=failed >> $GITHUB_OUTPUT")
    print(f"failure_reason={failure_reason} >> $GITHUB_OUTPUT")
    if summary:
        print(f"summary={summary} >> $GITHUB_OUTPUT")


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
        print(f"::set-output name=user_request::{result.user_request}")
        print(f"::set-output name=model_override::{result.model_override or ''}")
        print(f"::set-output name=max_turns_override::{result.max_turns_override or ''}")

    elif args.command == "build-prompt":
        prompt = build_prompt(
            user_request=args.user_request,
            issue_title=args.issue_title,
            issue_body=args.issue_body,
            issue_number=args.issue_number,
            repository=args.repository,
        )
        print(f"::set-output name=prompt::{prompt}")

    elif args.command == "run-agent":
        agent_result = run_agent(
            prompt=args.prompt,
            model=args.model,
            max_turns=args.max_turns,
            timeout=args.timeout,
        )
        print(f"result={agent_result['result']} >> $GITHUB_OUTPUT")
        print(f"failure_reason={agent_result['failure_reason']} >> $GITHUB_OUTPUT")

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
