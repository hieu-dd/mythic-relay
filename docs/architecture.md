# Architecture

## Purpose

Define a lean architecture for `mythic-relay` that delivers the full AI bug-fix + PR flow with minimal moving parts.

## Design principles

- Claude-only runtime in initial release
- Deterministic CLI commands for GitHub Actions chaining
- Explicit contracts between stages via typed models and step outputs
- Safe-by-default branch and output policies

## Logical layers

1. `cli`
   - Command entrypoints invoked by GitHub Actions
   - Examples: `parse-request`, `build-prompt`, `run-agent`, `finalize-success`
2. `core`
   - Pipeline stage engine and event model
   - Stage order and failure propagation
3. `github`
   - GitHub API wrapper (comments, reactions, PR ops)
   - Thread context loader
4. `prompt`
   - Slash command parsing and prompt composition
5. `agent`
   - Claude command builder, process runner, timeout and failure classifier
6. `gitops`
   - WIP branch detect/checkpoint and safety checks
7. `memory`
   - Per-comment run state persistence
8. `security`
   - Secret redaction and input/host validation

## Core contracts

### RunRequest
- `mode`: `github|local`
- `user_request`: normalized instruction text
- `coding_agent`: fixed to `claude-code` in v0.1
- `dry_run`, `verbose`

### RunContext
- `workspace`, `repo_name`, `item_num`, `item_type`
- `thread_context`
- `metadata`: `comment_id`, `progress_comment_id`, `wip_branch`, timestamps

### RunResult
- `success`
- `stage`
- `agent_result`
- `failure_reason`
- `attempts`, `repair_attempts_used`

## Pipeline stages

1. `initialize`
2. `collect_context`
3. `compose_prompt`
4. `run_agent`
5. `finalize`

Each stage emits events consumed by progress reporting.

## Initial component map

- `mythic_relay/cli/commands.py`
- `mythic_relay/core/pipeline.py`
- `mythic_relay/github/api.py`
- `mythic_relay/prompt/parser.py`
- `mythic_relay/prompt/compose.py`
- `mythic_relay/agent/claude_runner.py`
- `mythic_relay/gitops/branches.py`
- `mythic_relay/memory/store.py`
- `mythic_relay/security/redaction.py`

## Non-goals for v0.1

- Multi-agent routing
- Advanced autonomy profiles
- Scheduled maintenance bots
- Replay/simulation runtime
