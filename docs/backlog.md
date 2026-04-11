# Backlog

This backlog prioritizes delivery of the full bug-fix + PR flow first, while postponing advanced automation.

## Priority model

- `P0`: required for go-live
- `P1`: stabilization and hardening
- `P2`: deferred enhancements

## P0 — Core delivery

### MR-001 — Bootstrap project scaffold
- Background: A consistent Python foundation is required before feature work.
- Goal: Initialize `mythic-relay` with package layout, tooling, and base CI checks.
- Scope: `pyproject`, lint/type/test setup, baseline package structure.
- Acceptance Criteria:
  - `ruff`, `mypy`, `pytest` run in CI
  - package import works
- Estimate: 1 day
- Dependencies: none

### MR-002 — Implement CLI command surface
- Background: GitHub Actions needs deterministic small commands.
- Goal: Provide CLI commands for each orchestration step.
- Scope: `parse-request`, `build-prompt`, `run-agent`, `finalize-success`, `finalize-failure`.
- Acceptance Criteria:
  - Each command runnable independently via CLI
  - Outputs emitted in GitHub Actions format
- Estimate: 1 day
- Dependencies: MR-001

### MR-003 — GitHub API wrapper (comments/reactions)
- Background: Progress visibility and final reporting depend on comment APIs.
- Goal: Support comment lifecycle and reactions with safe validation.
- Scope: create/update comment, add reactions, read comment body.
- Acceptance Criteria:
  - Wrapper handles issue comments reliably
  - API errors are surfaced with actionable messages
- Estimate: 1 day
- Dependencies: MR-001

### MR-004 — Progress comment lifecycle
- Background: Users need transparent execution state.
- Goal: Create and update one progress comment through run stages.
- Scope: state renderer + transition updates + finalize status.
- Acceptance Criteria:
  - States progress from received to completed/failed
  - Final comment includes concise outcome summary
- Estimate: 1 day
- Dependencies: MR-003

### MR-005 — Parse `/ai` request and compose prompt
- Background: Agent quality depends on clean request parsing and context framing.
- Goal: Normalize request text and produce final prompt template.
- Scope: parse slash command and optional model/max-turns flags.
- Acceptance Criteria:
  - Correct parsing of `/ai <request>`
  - Prompt includes issue context and explicit PR objective
- Estimate: 1 day
- Dependencies: MR-002

### MR-006 — Claude runtime execution
- Background: This is the core action path that turns request into changes.
- Goal: Run Claude CLI with timeout, output capture, and failure classification.
- Scope: process runner, timeout control, error mapping.
- Acceptance Criteria:
  - Returns `auth_error`, `agent_timeout`, or `agent_error` correctly
  - Captured output is bounded and redacted
- Estimate: 1.5 days
- Dependencies: MR-002

### MR-007 — WIP branch detect and checkpoint
- Background: Automation must avoid writing directly to protected branches.
- Goal: Work only on `orchestrator/issue-<id>-wip` and push safely.
- Scope: branch detect/create/checkout, commit, push checks.
- Acceptance Criteria:
  - Run creates or reuses WIP branch
  - Changes are committed and pushed safely
- Estimate: 1 day
- Dependencies: MR-001

### MR-008 — Ensure PR creation path
- Background: Business value requires a PR output, not only local changes.
- Goal: Ensure agent flow consistently creates a PR.
- Scope: prompt instruction contract + permission + validation.
- Acceptance Criteria:
  - Successful run ends with PR URL
  - Failure clearly states why PR was not created
- Estimate: 0.5 day
- Dependencies: MR-005, MR-006, MR-007

### MR-009 — Build main GitHub workflow
- Background: End-to-end behavior must run from issue comments.
- Goal: Implement orchestrator workflow chaining all core commands.
- Scope: workflow YAML, step output validation, failure finalization.
- Acceptance Criteria:
  - `/ai ...` on issue executes full chain and produces PR
  - Failure path still updates progress comment
- Estimate: 1 day
- Dependencies: MR-002 through MR-008

## P1 — Stabilization

### MR-010 — Security essentials
- Background: Autonomous runs can leak secrets or accept unsafe input.
- Goal: enforce redaction, host allowlist, strict ID validation.
- Scope: security utilities + workflow guards.
- Acceptance Criteria:
  - No secret appears in comments/log snapshots
  - Invalid IDs fail fast
- Estimate: 1 day
- Dependencies: MR-003, MR-006

### MR-011 — Failure-safe finalization
- Background: Operators need reliable failure visibility.
- Goal: Always finalize with actionable reason when run fails.
- Scope: finalize-failure payload and fallback logic.
- Acceptance Criteria:
  - Progress never remains stale in active state after terminal failure
- Estimate: 0.5 day
- Dependencies: MR-004, MR-009

### MR-012 — Minimal memory persistence
- Background: Historical state is needed for reruns/debugging.
- Goal: Persist per-comment status and run logs.
- Scope: `.orchestrator/comment-<id>/status.json` + `run-log.md`.
- Acceptance Criteria:
  - New runs update persisted state consistently
- Estimate: 0.5 day
- Dependencies: MR-009

### MR-013 — Operator documentation
- Background: Fast incident handling reduces cycle time.
- Goal: Provide runbook and troubleshooting guides.
- Scope: update README + operator playbook.
- Acceptance Criteria:
  - On-call can triage common failures within 5 minutes
- Estimate: 0.5 day
- Dependencies: MR-009

## P2 — Deferred enhancements

- Confirmation flow (`/ai yes`, `/ai no`)
- Cancel flow (`/ai cancel`)
- Label trigger `ai:claude`
- Basic metrics emission
- Replay/simulate local tooling
