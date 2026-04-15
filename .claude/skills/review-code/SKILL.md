---
name: review-code
description: |
  Comprehensive code review skill covering code quality, bugs, security, performance, and project-specific patterns.
  Use when the user asks to: review code, check a file, look for bugs, audit security, analyze code quality,
  or any variant of "review this", "check my code", "is this correct", "what's wrong here".
  Covers Python, GitHub Actions YAML, CLI/subprocess patterns, and GitHub API usage as found in this project.
---

# Review Code

## Workflow

1. Read the target file(s) if not already in context
2. Identify the file type(s) — see checklist references below
3. Run through every applicable checklist section
4. For `github.com` PR reviews, split findings into issue-level comments with exact file/line locations via GitHub MCP tools
5. For `github.com` PR reviews, post one concise PR summary comment (no full detailed report)
6. For non-PR reviews, produce a structured report (see Output Format)

For each file type, load the relevant reference:
- **Python** (`.py`) → read `references/python.md`
- **GitHub Actions YAML** (`.github/workflows/*.yml`) → read `references/gha-yaml.md`
- **Security audit** (any file, or when user asks specifically) → read `references/security.md`

## PR Comment Requirement (Mandatory)

- If the user asks to review a `github.com` PR (URL or PR number), you MUST use GitHub MCP tools to post comments.
- Each finding MUST be posted as a separate issue comment, anchored to the most accurate file/line in the diff.
- Do not combine all findings into one long PR comment.
- Post one additional PR-level summary comment with overall status, risk highlights, and verdict.
- Keep the PR-level summary concise; detailed fixes belong in the issue-level comments.
- Use GitHub MCP as the primary path for posting comments. Do not use CLI-based PR commenting as a substitute when MCP is available.
- If GitHub MCP is unavailable or fails, clearly report the blocker and return a ready-to-paste PR comment body.
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
