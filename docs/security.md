# Security

## Purpose

Capture minimum security controls required for autonomous code changes in CI.

## Secret handling

- Never print raw tokens in logs/comments
- Redact known secret env values before persistence
- Redact token-like patterns in agent output

## Host validation

- GitHub API base URL must be HTTPS
- Host must be in explicit allowlist

## Input validation

- `comment_id` and `item_num` must be numeric
- Reject malformed repo identifiers
- Reject empty required env inputs early

## Git guardrails

- Allow pushes only to `relay/*`
- Block destructive branch operations unless explicitly approved

## Permission model (GitHub Actions)

Minimum permissions:

- `contents: write` (WIP branch + PR path)
- `issues: write` (progress comments)
- `pull-requests: write` (PR metadata and comments)

## Security acceptance checks

- No secret appears in final progress comment
- No push to base/protected branch from automation
- Invalid IDs fail fast with clear error
