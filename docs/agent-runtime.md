# Agent Runtime (Claude-Only)

## Purpose

Define how `mythic-relay` runs Claude Code safely and predictably inside GitHub Actions.

## Runtime model

- Backend: `claude-code` only (v0.1)
- Invocation style: subprocess command with strict timeout
- Input: composed prompt + item metadata
- Output: captured logs/result with truncation and redaction

## Command contract

Expected command shape:

```bash
claude -p --dangerously-skip-permissions --model <model> --max-turns <n> -- <prompt>
```

## Required environment

- `LY_CHATAI_PAT` / proxy auth secret
- `CLAUDE_MODEL`
- `CLAUDE_MAX_TURNS`
- `TIMEOUT_MINUTES`

## Failure classification

- `auth_error`: unauthorized/forbidden/authentication failed
- `agent_timeout`: process exceeds timeout
- `agent_error`: non-zero exit not mapped to auth/timeout

## Output handling

- Stream stdout/stderr for observability
- Capture bounded output size for step outputs/comments
- Redact secrets before persistence/commenting

## PR creation behavior

The agent is expected to:

1. Implement code changes
2. Commit on WIP branch
3. Push `relay/issue-<id>-wip`
4. Create PR with `gh pr create`

Prompt must explicitly require PR creation to make this deterministic.

## Deferred runtime features

- Multi-agent fallback
- Auto-repair loops beyond minimal retries
- Replay and simulation modes
