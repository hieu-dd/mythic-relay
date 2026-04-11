# GitOps and Branching

## Purpose

Define safe git behavior for autonomous code changes.

## Branch strategy

- Base branch remains untouched by automation
- Work branch format: `orchestrator/issue-<issue_number>-wip`

Example:

- Issue `#128` -> `orchestrator/issue-128-wip`

## Branch lifecycle

1. Detect remote WIP branch
2. If exists: fetch and checkout
3. If missing: create local branch from base
4. Agent commits changes
5. Push branch to origin
6. Create PR from WIP branch to base

## Safety rules

- Reject pushes to non-`orchestrator/*` branches
- Do not force-push protected branches
- Validate issue number as digits only

## Checkpoint behavior

- On successful code edits, checkpoint commit is created
- On failure, best-effort checkpoint can still be attempted when safe

## Deferred behavior

- Dedicated memory branch (`*-memory`)
- Automatic stale branch cleanup jobs
