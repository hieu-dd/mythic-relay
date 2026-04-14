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
4. Produce a structured report (see Output Format)
5. Post the report as a PR comment via GitHub MCP tools

For each file type, load the relevant reference:
- **Python** (`.py`) → read `references/python.md`
- **GitHub Actions YAML** (`.github/workflows/*.yml`) → read `references/gha-yaml.md`
- **Security audit** (any file, or when user asks specifically) → read `references/security.md`

## PR Comment Requirement (Mandatory)

- If the user asks to review a `github.com` PR (URL or PR number), you MUST publish the review as a PR comment using GitHub MCP tools.
- Use GitHub MCP as the primary path for posting review comments. Do not use CLI-based PR commenting as a substitute when MCP is available.
- Post the same structured content defined in Output format as the comment body.
- If GitHub MCP is unavailable or fails, clearly report the blocker and return a ready-to-paste PR comment body.
- This requirement applies only to `github.com` pull requests.

## Output format

Use this structure for every review:

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

## Scope guidance

- Report findings at the line level when possible (`file.py:42`)
- Be specific: name the variable, function, or pattern that is wrong
- For security findings, always explain the attack vector
- Do not invent issues — only flag what is demonstrably wrong or risky
- When unsure, note the uncertainty rather than guessing
