# Code Review — Quick Reference

## Trigger Detection

| Input | Trigger? |
|---|---|
| `review this file` / `check my code` | ✅ Local review |
| `github.com/owner/repo/pull/123` | ✅ PR review |
| Raw PR number (`42`) | ✅ PR review (resolve via GitHub MCP) |
| `/review-pr 42` | ✅ PR review |
| `find bugs in X` | ✅ Local review |
| `audit security of Y` | ✅ Security-focused review |

If PR review: use GitHub MCP to post issue-level comments + 1 summary comment.

## Review Depth Decision

```
Single function / small diff / targeted question?
├── Yes → Quick scan (Critical items only, brief verdict)
└── No → Deep review (all sections, full structured report)

Default to deep review unless user says "quick" or "just check X".
```

## MR Number → File Path Map

| MR | File |
|---|---|
| MR-002 | `mythic_relay/cli/commands.py` |
| MR-003 | `mythic_relay/github/api.py` |
| MR-006 | `mythic_relay/agent/claude_runner.py` |
| MR-007 | `mythic_relay/gitops/branches.py` |
| MR-010 | `mythic_relay/security/redaction.py` |
| MR-012 | `mythic_relay/memory/store.py` |

## Verdict Guidance

| Verdict | When to use |
|---|---|
| **✅ Approve** | No critical or warning findings |
| **🔄 Approve with suggestions** | Warnings present but non-blocking |
| **❌ Needs changes** | Critical issue found (bug, security vuln, data loss risk) |

## PR Comment Format (MCP failure fallback)

```markdown
**🔴 [file:line] Severity: Title**

Problem: ...
Impact: ...
Fix: ...
```

Summary comment at PR level:
```markdown
## Review Summary
- Critical: N | Warnings: N | Suggestions: N
**Verdict:** ✅ / 🔄 / ❌
```

## Reference Paths

- Python checklist → `.claude/skills/review-code/references/python.md`
- GHA YAML checklist → `.claude/skills/review-code/references/gha-yaml.md`
- Security checklist → `.claude/skills/review-code/references/security.md`

## Key Project-Specific Rules

- Always check `subprocess.run()` has `timeout=` and no `shell=True`
- GitHub Actions: `pull_request_target` + `checkout` = critical injection risk
- Branch pushes must be to `relay/issue-<id>-wip` only
- Issue body / `/ai` request text = untrusted, must be delimited in prompts
- `.relay/` state files must not contain raw API responses or secrets