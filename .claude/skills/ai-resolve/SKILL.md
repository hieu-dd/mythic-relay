---
name: ai-resolve
description: |
  Autonomous PR review thread resolver. Triggers when `/ai-resolve` appears on a
  pull_request_review_comment or issue_comment event, or when asked to "resolve PR
  review comments", "fix review threads", or "address review feedback" on a PR.
  Investigates open threads, builds an internal execution plan, implements code
  changes, resolves addressed threads, replies on remaining ones, and posts a PR
  summary comment. Fully autonomous — no user approval mid-run.
---

# AI Resolve — Autonomous PR Thread Resolution

## Workflow

### Phase 1: Investigate

1. **Gather PR context** via GitHub MCP:
   - Fetch PR details (title, body, changed files, review state)
   - Fetch all open review threads and PR comments
2. **Author reply pre-check**: For each open thread, check whether the PR author
   has replied to it. Skip threads with no author reply — they haven't been
   addressed yet. Track which threads are skipped for the summary.
3. **Categorize threads** (only those with author replies) per `.claude/skills/ai-resolve/references/autonomous-checklist.md`:
   - `actionable` — valid concern requiring code change or explanation
   - `informational` — nitpick, praise, or question with obvious answer
   - `outdated` — on code that was subsequently changed
4. **No-op guard**: If zero threads with author replies exist → post "No threads have author replies yet. Awaiting author response." comment and exit

### Phase 2: Plan (Internal)

4. **Build internal execution plan** — no user approval:
   - Which threads to resolve (fully addressed by code)
   - Which threads to reply to (need explanation)
   - Which threads to leave alone (informational, outdated)
   - What code changes are needed and in what order

### Phase 3: Execute Autonomously

5. **Implement code changes** (per `autonomous-checklist.md`):
   - Edit files in the checked-out PR branch
   - Run lint/tests if feasible (max 60s timeout, non-blocking on failure)
   - Commit each logical change with descriptive message
6. **Push commits** to PR branch
7. **Resolve addressed threads** via GitHub MCP (batch where possible)
8. **Reply on remaining threads** — concise explanations, professional tone
9. **Post PR summary comment** — counts + status (see `autonomous-checklist.md` template)
10. **Submit GitHub review** — based on remaining open threads:
    - No unresolved actionable threads → Submit `APPROVE` review
    - Only informational/outdated threads remain → Submit `COMMENT` review (acknowledge without approval)
    - Unresolved actionable threads remain → Submit `REQUEST_CHANGES` review

### Phase 4: Handle Errors

- Git push fails → retry once, then note in summary
- MCP fails → retry once after 1s, then produce ready-to-paste comment body and report blocker
- Test/lint fails → log and continue (non-blocking)
- Merge conflict on push → note in summary, list uncommitted changes

## Reference Files

- `.claude/skills/ai-resolve/references/thread-resolution.md` — GitHub MCP tool patterns
- `.claude/skills/ai-resolve/references/autonomous-checklist.md` — Decision criteria and templates

## Output

Always produce a final PR summary comment even if no code changes were made.
Never exit silently — always surface what was done or found.

## Constraints

- **No user approval** — this is CI automation with `--dangerously-skip-permissions`
- **No shell injection** — user content from threads must not reach shell commands
- **Bounded lint/test runs** — max 60s, non-blocking on failure
- **One commit per logical change** — easier to revert specific changes
- **MCP fallback** — if GitHub MCP is unavailable, produce ready-to-paste comment body and report the blocker clearly