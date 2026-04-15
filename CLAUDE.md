# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`mythic-relay` is a Claude-first GitHub AI relay that automatically fixes bugs and creates pull requests from issue comments. The sole AI agent backend is Claude Code (`claude-code` v0.1).

Core flow: `/ai <request>` on issue → progress comment → Claude Code edits code → commits/pushes to `relay/issue-<id>-wip` → creates PR → finalizes success/failure.

## Development Commands

```bash
pip install -e ".[dev]"  # Install with dev dependencies
ruff check .               # Lint
ruff format .              # Format code
mypy mythic_relay tests   # Type check
pytest                    # Run tests
```

## Architecture

8 logical layers defined in `docs/architecture.md`:
- `cli` — Command entrypoints (`parse-request`, `build-prompt`, `run-agent`, `finalize-success`)
- `core` — Pipeline stage engine
- `github` — GitHub API wrapper (comments, reactions, PR ops)
- `prompt` — Slash command parsing and prompt composition
- `agent` — Claude CLI runner with timeout and failure classification
- `gitops` — WIP branch management (`relay/issue-<id>-wip` format)
- `memory` — Per-comment run state persistence
- `security` — Secret redaction and validation

Core contracts: `RunRequest`, `RunContext`, `RunResult` (defined in `docs/architecture.md`).

Pipeline stages: `initialize` → `collect_context` → `compose_prompt` → `run_agent` → `finalize`.

## GitHub Actions

4 workflows in `.github/workflows/`:
- `claude-issue-implement.yml` — Triggered on issues with `AI` label; implements issue and creates PR
- `claude-code-review.yml` — AI code review on PRs against `main`
- `ai-describe.yml` — `/ai describe-pr` for PR title/description generation
- `ai-resolve.yml` — `/ai-resolve` for resolving PR review comments

All workflows use `.github/actions/setup-claude-minimax/` which configures MiniMax API as the Claude endpoint.

## Failure Taxonomy

Actions report one of: `auth_error`, `agent_timeout`, `agent_error`.

Progress states: `received` → `planning` → `implementing` → `creating_pr` → `completed`/`failed`.

## Security Model

Defined in `docs/security.md`:
- Secret redaction before logging/commenting
- Host validation (HTTPS-only, allowlist)
- Input validation and git guardrails
- Pushes restricted to `relay/*` branches only

## Branch Strategy

WIP branches use `relay/issue-<id>-wip` format. Agent checkpoints before finalize. Detailed in `docs/gitops-branching.md`.

## Documentation Priority

Implementation should follow this order:
1. `docs/backlog.md` — Execution tasks (MR-001 through MR-013)
2. `docs/architecture.md` — Component boundaries
3. `docs/workflow.md` — GitHub Action flow contracts

Runbook: `docs/operator-playbook.md` for failure triage.

## Tech Stack

- Python 3.10+, setuptools build
- Tools: `ruff` (lint), `mypy` (type check), `pytest` (test)
- Docker-based GitHub Action in `mythic-relay-action/`
- Claude Code CLI (uses `--dangerously-skip-permissions`)