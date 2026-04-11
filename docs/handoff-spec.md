# Mythic Relay - Handoff Specification

## 1) Goal
Build a Python-based automation system that processes engineering requests from GitHub (issues/PRs/comments/labels/schedules), runs a coding agent, tracks progress transparently, checkpoints work safely, and finalizes with a clear outcome.

## 2) Scope
### In scope
- Slash command requests (`/ai ...`)
- Agent backend selection (`opencode`, `codex`, `claude-code`)
- Progress comment lifecycle
- Risk confirmation flow (`/ai yes`, `/ai no`)
- Cancel flow (`/ai cancel`)
- Trusted label triggers
- Scheduled triggers
- WIP and memory branch management
- Metrics and operational logs

### Out of scope
- No migration of old source code
- No line-by-line implementation parity requirement
- No UI/frontend scope

## 3) Features and detailed flows

## F01 - Slash command intake
Purpose: turn a GitHub comment into an executable run.

Flow:
1. Receive `issue_comment` or `pull_request_review_comment` event.
2. Validate comment starts with `/ai` (case-insensitive).
3. Validate user trust/association.
4. Lock by per-item concurrency key.
5. Start main processing pipeline.

## F02 - Trigger classification
Purpose: route request vs confirmation vs cancel.

Flow:
1. Normalize comment text.
2. If `/ai cancel`: route to cancel flow.
3. If `/ai yes` or `/ai no`: route to confirmation flow.
4. If `/ai-...`: ignore.
5. Else if `/ai ...`: route to request flow.

## F03 - Agent backend resolution
Purpose: pick the correct coding backend.

Flow:
1. Read explicit backend input if provided.
2. Else parse backend from command body.
3. Normalize aliases (for example `claude` -> `claude-code`).
4. Validate against allowed backends.
5. Fallback to default backend.

## F04 - Per-request overrides
Purpose: allow `--model` and `--max-turns` in the request.

Flow:
1. Parse `--model <value>`.
2. Parse `--max-turns <value>`.
3. Remove those flags from final user request text.
4. Apply overrides only for current run.
5. Keep global defaults unchanged.

## F05 - Progress comment lifecycle
Purpose: maintain one live status location.

Flow:
1. Add `eyes` reaction on trigger comment.
2. Create progress comment.
3. Set initial state to `received`.
4. Supersede stale in-progress comments if needed.
5. Persist progress comment id and start timestamp.

## F06 - Thread context collection
Purpose: provide compact and relevant historical context.

Flow:
1. Fetch recent issue and/or review comments.
2. Exclude current trigger comment and progress comment.
3. Prefer comments newer than prior run timestamp.
4. Keep only latest N comments.
5. Truncate to max char budget.

## F07 - Item context resolution
Purpose: determine target entity and id.

Flow:
1. Map event type to item type (`Issue`/`PR`).
2. Resolve item number from payload.
3. Validate numeric format.
4. Attach item context to run metadata.
5. Fail fast if missing/invalid.

## F08 - WIP and memory branch management
Purpose: isolate work safely and preserve memory.

Flow:
1. Compute deterministic WIP branch name.
2. Checkout existing WIP branch or create one.
3. Rebase from base branch if enabled.
4. Restore memory content when available.
5. Continue run on WIP branch.

## F09 - Decision policy and risk gate
Purpose: auto-run safe requests, require confirmation for risky ones.

Flow:
1. Evaluate risk signals (secret/security/destructive/high-impact).
2. If missing secret: mark `blocked_missing_secret`.
3. If risky: mark `needs_confirmation`.
4. Else: mark `can_autodecide`.
5. Set `risk_tier` for the run.

## F10 - Confirmation flow
Purpose: pause and resume reliably.

Flow:
1. Persist state as `awaiting_confirmation`.
2. Persist resume request + backend overrides.
3. Post confirmation instructions.
4. On `/ai yes`: resume saved request.
5. On `/ai no` or timeout: finalize as failed with reason.

## F11 - Prompt composition
Purpose: generate execution prompt with all required context.

Flow:
1. Load prompt template.
2. Inject sanitized user request.
3. Inject compact thread context.
4. Inject persisted run memory.
5. Inject autonomy/risk/retry guidance.

## F12 - Agent execution
Purpose: run coding backend with controlled environment.

Flow:
1. Setup backend runtime and pinned version.
2. Prepare constrained environment variables.
3. Execute backend command with selected model.
4. Capture output and exit code.
5. Classify failure reason.

## F13 - Automatic repair retries
Purpose: recover from common verification failures.

Flow:
1. Detect category (`lint`, `typecheck`, `test`, `build`).
2. Check retry eligibility by policy.
3. Build minimal repair prompt.
4. Retry until success or retry limit.
5. Update progress each retry.

## F14 - Checkpointing
Purpose: avoid losing progress between runs.

Flow:
1. Commit/push code changes to WIP branch.
2. Commit/push memory files to memory branch.
3. Record checkpoint status.
4. Return to working branch.
5. Continue/finalize run.

## F15 - Finalization
Purpose: close run with clear, auditable result.

Success flow:
1. Update progress to `Completed`.
2. Attach concise final result.
3. Change reaction from `eyes` to `rocket`.

Failure flow:
1. Update progress to `Failed`.
2. Include failure reason and recovery hint.
3. Change reaction from `eyes` to `confused`.

## F16 - Cancel flow
Purpose: stop active queued/running jobs for the same item.

Flow:
1. Receive trusted `/ai cancel` command.
2. List active runs (`queued`, `in_progress`).
3. Filter by workflow and item concurrency key.
4. Cancel matching runs.
5. Post cancellation summary.

## F17 - Trusted issue-label trigger
Purpose: start runs from trusted labels.

Flow:
1. Receive `issues:labeled` event.
2. Validate label in supported set.
3. Validate sender permission.
4. Map label to backend and default request.
5. Launch normal pipeline.

## F18 - Trusted PR review-label trigger
Purpose: run AI review from label-driven trigger.

Flow:
1. Receive PR label event.
2. Validate trusted sender.
3. Start review-oriented run.
4. Maintain progress updates.
5. Finalize with review outcome.

## F19 - Scheduled request trigger
Purpose: auto-trigger runs for labeled open issues.

Flow:
1. Run on cron/schedule.
2. Query open issues with designated labels.
3. Skip PR items.
4. If missing trigger comment, post one.
5. Let standard request flow continue.

## F20 - Daily health check
Purpose: detect dependency and workflow health issues.

Flow:
1. Collect outdated/audit/actions findings.
2. Aggregate result counts.
3. Upload report artifacts.
4. Upsert rolling issue if findings exist.
5. Close rolling issue if findings are resolved.

## F21 - Daily auto-fix maintenance
Purpose: apply safe patch-level updates automatically.

Flow:
1. Trigger after health check.
2. Load findings artifact.
3. Select patch-safe update candidates.
4. Apply updates.
5. Run validations.
6. If pass: create branch/commit/PR.
7. If fail: open follow-up issue.

## F22 - Weekly tool/version maintenance
Purpose: keep agent/tool versions current.

Flow:
1. Create weekly maintenance request.
2. Run maintenance pipeline.
3. Update pinned versions.
4. Summarize release context.
5. Create/update maintenance PR.

## F23 - Metrics and observability
Purpose: track reliability and autonomy outcomes.

Flow:
1. Emit structured events at major transitions.
2. Compute run duration metrics.
3. Record confirmation and retry counts.
4. Normalize and record failure reasons.
5. Export metrics to logs/artifacts.

## F24 - Memory persistence per request thread
Purpose: resume future runs with context continuity.

Flow:
1. Write `status.json`.
2. Write `snapshot.md`.
3. Append `run-log.md`.
4. Compact logs periodically.
5. Reload memory on next run.

## F25 - Stale WIP branch cleanup
Purpose: keep repository branch list healthy.

Flow:
1. Run cleanup on schedule/manual trigger.
2. Compute stale threshold.
3. Find stale WIP branches.
4. Delete eligible stale branches.
5. Publish cleanup summary.

## 4) Standard run states
- `received`
- `researching`
- `planning`
- `implementing`
- `creating_pr` (if applicable)
- `awaiting_confirmation` (if applicable)
- `completed` | `failed` | `cancelled`

## 5) Standard failure reasons
- `auth_error`
- `agent_timeout`
- `agent_error`
- `confirmation_timeout`
- `confirmation_rejected`
- `invalid_confirmation_state`
- `blocked_missing_secret:<name>`

## 6) Definition of done
1. End-to-end request flow works from trigger to finalize.
2. Confirmation flow works correctly for `/ai yes` and `/ai no`.
3. Cancel flow stops correct active runs.
4. Progress comment always reflects real run status.
5. WIP and memory checkpointing are reliable.
6. Logging and metrics are sufficient for operations.
7. Label and schedule triggers work under trust policy.
