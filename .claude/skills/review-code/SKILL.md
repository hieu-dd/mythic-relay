---
name: review-code
description: |
  Comprehensive code review skill covering code quality, bugs, security, performance, and project-specific patterns.
  Use when the user asks to: review code, check a file, look for bugs, audit security, analyze code quality,
  or any variant of "review this", "check my code", "is this correct", "what's wrong here", "assess this PR".
  Also triggers on GitHub PR URLs (e.g. github.com/owner/repo/pull/123) or raw PR numbers (e.g. "/review-pr 42").
  Covers Python, GitHub Actions YAML, CLI/subprocess patterns, and GitHub API usage as found in this project.
---

# Review Code

## Workflow

1. **Detect trigger** — Identify whether this is:
   - A GitHub PR review (URL like `github.com/owner/repo/pull/123`, or raw PR number)
   - A local/single-file review (explicit file path or "review this" with no PR context)
   - A quick-scan request (targeted question about a specific pattern, not a full file)
2. **Determine depth** — See Review Depth Guide below before running checklists
3. **Read the target file(s)** if not already in context
4. **Identify the file type(s)** — see checklist references below
5. **Run through every applicable checklist section** (skip optional items on quick scans)
6. For `github.com` PR reviews: post findings via GitHub MCP tools (see PR Comment Requirement)
7. For non-PR reviews: produce a structured report (see Output Format)

For each file type, load the relevant reference:
- **Python** (`.py`) → read `.claude/skills/review-code/references/python.md`
- **GitHub Actions YAML** (`.github/workflows/*.yml`) → read `.claude/skills/review-code/references/gha-yaml.md`
- **Security audit** (any file, or when user asks specifically) → read `.claude/skills/review-code/references/security.md`

Reference paths are relative to the project root.

## Review Depth Guide

**Quick scan** — A single-file, targeted, or partial review (e.g. "check this function", one specific pattern, or PR with few changes):
- Run only Critical items from checklists
- Skip optional/suggestion items
- Produce brief verdict

**Deep review** — Full file or multi-file review (e.g. full PR, architecture assessment, security audit):
- Run all checklist sections including Warnings and Suggestions
- Cross-reference with project-specific references (MR-### anchors)
- Full structured report

Default to deep review unless the user explicitly asks for a quick scan.

## PR Comment Requirement (Mandatory)

- If the user asks to review a `github.com` PR (URL or PR number), you MUST use GitHub MCP tools to post comments.
- Each finding MUST be posted as a separate issue comment, anchored to the most accurate file/line in the diff.
- Do not combine all findings into one long PR comment.
- Post one additional PR-level summary comment with overall status, risk highlights, and verdict.
- Keep the PR-level summary concise; detailed fixes belong in the issue-level comments.
- Use GitHub MCP as the primary path for posting comments. Do not use CLI-based PR commenting as a substitute when MCP is available.
- **MCP fallback**: If GitHub MCP is unavailable or fails, retry once after a brief pause. If it still fails, produce a ready-to-paste multi-finding comment body (same format as issue-level comments would take) and clearly report the MCP blocker so the user can manually post.
- This requirement applies only to `github.com` pull requests.

## Output format

Use this structure for non-PR reviews:

```
## Code Review: <filename>

### Summary
One paragraph: overall health, biggest concerns, notable strengths.

### Critical  🔴
Issues that must be fixed before merging — bugs, security vulnerabilities, data loss risk.
- [file:line] Description of the issue. **Fix:** concrete suggestion.

### Warnings  🟡
Code quality, reliability, or maintainability problems that should be addressed.
- [file:line] Description. **Fix:** concrete suggestion.

### Suggestions  🔵
Style, performance, and improvement opportunities. Optional but valuable.
- [file:line] Description. **Fix:** concrete suggestion.

### Verdict
One of: ✅ Approve | 🔄 Approve with suggestions | ❌ Needs changes
```

If a section has no findings, omit it entirely — don't write "None found."

For `github.com` PR reviews, use this posting model:

1. Issue-level comments (one per finding, anchored to file/line)
   - Title: severity + short issue label
   - Body: problem, impact, and concrete fix
   - Include exact location (`file:line`) in the comment text even when anchored
2. PR-level summary comment
   - Short summary of overall code health
   - Counts by severity (critical/warning/suggestion)
   - Final verdict: ✅ Approve | 🔄 Approve with suggestions | ❌ Needs changes
   - Do not repeat full finding details here

## Scope guidance

- Report findings at the line level when possible (`file.py:42`)
- Be specific: name the variable, function, or pattern that is wrong
- For security findings, always explain the attack vector
- Do not invent issues — only flag what is demonstrably wrong or risky
- When unsure, note the uncertainty rather than guessing
