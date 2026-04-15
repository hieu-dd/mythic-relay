# Autonomous Resolution Checklist

## Thread Categorization Decision Tree

```
For each open review thread:
│
├── Is the thread on code that still exists in the PR?
│   ├── NO → Mark as `outdated`. Do not resolve or reply.
│   └── YES ↓
│
├── Does the thread express a valid concern (bug, design issue, missing tests)?
│   ├── YES → Mark as `actionable`. Code change or explanation needed.
│   └── NO ↓
│
├── Is it purely informational (nitpick, praise, question with obvious answer)?
│   ├── YES → Mark as `informational`. Reply briefly or leave alone.
│   └── NO ↓
│
└── Default → Mark as `informational`. Use judgment.
```

## Code Change Execution Checklist

1. **Identify files** that need changes to address actionable threads
2. **Read relevant files** in the checked-out branch
3. **Plan edits** — one logical change per commit
4. **Edit files** — use Claude Code tool suite (edit, write, etc.)
5. **Run lint/tests** if feasible:
   - Only run if changed files have associated tests
   - Timeout: max 60 seconds per test run
   - On failure: continue without blocking — tests may be pre-existing failures
6. **Commit each change** with descriptive message:
   ```
   [thread-id] Address review comment: <one-line summary>

   - What changed and why
   - Reference the thread ID if available
   ```
7. **Push commits** to PR branch using local git

## Thread Resolution vs. Reply Criteria

| Situation | Action |
|---|---|
| Code change fully addresses the concern | Resolve thread (no reply) |
| Code change partially addresses concern | Resolve thread + reply explaining what was done |
| Concern requires explanation, no code change | Reply only, leave thread open |
| Disagreement with the feedback | Reply with reasoning, leave open |
| Informational comment | Reply briefly or ignore |
| Outdated thread | Do nothing — don't resurrect it |

## Summary Comment Template

```markdown
## AI Resolve Summary

**Commits pushed:** N
**Threads resolved:** N
**Threads replied:** N
**Remaining open:** N

### Resolved
- [thread] <brief description of what was fixed>

### Replied
- [thread] <brief description of what was explained>

### Remaining
- [thread] <brief description of what needs attention>
```

## Error Handling

| Error | Response |
|---|---|
| Git push fails | Retry once; if still fails, post summary with commit count and note that push failed |
| MCP call fails | Retry once after 1s; if still fails, fall back to producing ready-to-paste comment body |
| Test/lint fails | Log but continue — do not block on pre-existing test failures |
| No actionable threads found | Post "No actionable review threads found. PR looks good." — do not leave silent |
| Git merge conflict on push | Post summary noting conflict needs manual resolution, list uncommitted changes |

## No-Op Guard

Before starting any work:
- Fetch all open threads
- If zero actionable threads exist → post "No actionable review threads found." comment and exit successfully
- Do not run Claude agent on the codebase if there's nothing to do