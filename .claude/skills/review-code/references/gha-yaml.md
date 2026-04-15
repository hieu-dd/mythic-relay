# GitHub Actions YAML Review Checklist

## Project Workflow Map
Reference these when reviewing specific workflows:
- `claude-issue-implement.yml` — Triggered by `AI` label on issues; runs `/ai` request → Claude Code → PR
- `claude-code-review.yml` — AI code review on PRs against `main`
- `ai-describe.yml` — `/ai describe-pr` for PR title/description generation
- `ai-resolve.yml` — `/ai-resolve` for resolving PR review comments

All workflows use `.github/actions/setup-claude-minimax/` which configures MiniMax API as the Claude endpoint.

## Review Depth
- **Quick scan** (trigger check, permission audit): Trigger safety, Permissions, Secrets handling sections only
- **Full audit**: All sections below

## Trigger safety
- `pull_request_target` with `checkout` of PR head = critical injection risk — flag immediately
- `workflow_dispatch` inputs validated before use in shell steps
- `push` triggers scoped to specific branches — not `**` or omitted
- Issue comment trigger (`issue_comment`) checks that commenter has write permission before acting

## Permissions
- `permissions:` block present and minimal — principle of least privilege
- `contents: write` only on steps that actually commit/push
- `pull-requests: write` only on steps that create/update PRs
- `issues: write` only on steps that post comments
- No `write-all` or `permissions: write-all`

## Secrets handling
- Secrets accessed via `${{ secrets.NAME }}` — never hardcoded
- Secrets not echoed in `run:` steps (no `echo ${{ secrets.TOKEN }}`)
- `GITHUB_TOKEN` used instead of PAT where sufficient
- Outputs that may contain secrets masked with `::add-mask::`

## Step output chaining (project-specific: MR-009)
- Step outputs use `echo "key=value" >> $GITHUB_OUTPUT` (new syntax, not `set-output`)
- Each step's output validated before use in downstream steps
- `if: failure()` steps present for finalization on failure path
- Failure finalization step always runs: `if: always()` or `if: failure()`

## Branch guardrails (project-specific: MR-007)
- Workflow checks that target branch matches `relay/issue-*-wip` pattern before push
- No direct commits to `main` or `master` from automation
- Branch creation is idempotent — `git checkout -B` or explicit existence check

## Reliability
- `timeout-minutes:` set on every **job** — never unbounded
- Individual long steps also have `timeout-minutes:` (defense in depth)
- `continue-on-error: true` used sparingly and only where intentional
- Environment variables scoped to the step that needs them, not the whole job

## Dependency pins
- Third-party actions pinned to full SHA, not mutable tag (`uses: actions/checkout@abc1234`)
- First-party (`actions/*`) may use version tags
- No `@master` or `@main` for third-party actions

## Concurrency
- `concurrency:` group defined to prevent duplicate runs on the same issue
- `cancel-in-progress: true` set where re-runs should cancel stale jobs
