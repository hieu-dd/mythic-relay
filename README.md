# mythic-relay

Claude-first GitHub AI orchestrator for fixing bugs and creating pull requests from issue comments.

## Why this project

`mythic-relay` is a new greenfield orchestrator inspired by the ai-orchestrator model, but optimized for fast delivery:

- Single agent backend in v0.1: `claude-code`
- Full core flow: receive request -> run AI fix -> commit/push -> create PR
- Minimal but strict safety: branch guardrails, secret redaction, structured failures

Advanced automation (auto-fix schedules, multi-agent profiles, replay/simulate) is intentionally postponed.

## Core workflow (v0.1)

1. User comments on an issue: `/ai <request>`
2. Action creates a progress comment and gathers thread context
3. Orchestrator builds a prompt and runs Claude Code
4. Agent edits code, commits, pushes to `orchestrator/issue-<id>-wip`
5. Agent creates PR via `gh pr create`
6. Action finalizes progress as success/failure with concise reason

## Repository structure

```text
mythic-relay/
  README.md
  docs/
    architecture.md
    workflow.md
    agent-runtime.md
    gitops-branching.md
    security.md
    operator-playbook.md
    backlog.md
    roadmap.md
```

## Scope decisions

- Keep: AI fix bug + create PR end-to-end
- Keep: progress visibility and clear failure taxonomy
- Keep: WIP branch strategy
- Postpone: scheduled auto-fix flows, multi-agent support, replay/simulate

## Getting started (documentation-first phase)

This repository currently focuses on product/technical design and execution backlog.

Implementation should follow:

1. `docs/backlog.md` (execution tasks)
2. `docs/architecture.md` (component boundaries)
3. `docs/workflow.md` (GitHub Action flow contracts)

## Success criteria for v0.1

- From an issue comment, AI can produce a PR on a safe WIP branch
- Progress comment reflects run states clearly
- Failure states are actionable (`auth_error`, `agent_timeout`, `agent_error`)
- No secrets are leaked in comments/log outputs
