# Roadmap

## Product direction

Deliver a reliable Claude-first GitHub issue-to-PR pipeline before adding advanced automation.

## Milestone A — Core go-live (Week 1)

Target outcome:

- Issue comment `/ai ...` can produce a PR on WIP branch with progress tracking.

Backlog included:

- MR-001 through MR-009

Go-live checks:

- End-to-end run succeeds on pilot repository
- PR URL produced in successful run
- Failure path still finalizes progress

## Milestone B — Stabilization (Week 2, first half)

Target outcome:

- Safer and easier operation in production-like usage.

Backlog included:

- MR-010 through MR-013

Go-live checks:

- Secret redaction validated
- Operator runbook tested in dry incidents

## Milestone C — Controlled expansion (Week 2, second half+)

Target outcome:

- Add selective advanced features based on usage pain points.

Candidate backlog:

- Confirmation flow
- Cancel flow
- Label triggers
- Metrics

## Release plan

- `v0.1.0`: Milestone A + B
- `v0.2.0`: selected Milestone C features based on operational demand
