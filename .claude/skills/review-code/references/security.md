# Security Review Checklist

## Secret leakage (project-specific: MR-010)
- No secret, token, or credential appears in:
  - GitHub issue/PR comments (via comment body or API response logged)
  - Log output captured by subprocess runner
  - Exception messages surfaced to the user
  - `.relay/` persisted state files
- Redaction applied before any output is stored or posted
- Environment variable names for secrets are not logged (even the name can be a hint)

## Input validation — issue IDs and user requests
- Issue IDs validated as integers before use in branch names or API calls
  - Invalid IDs must fail fast with a clear error, not panic or produce malformed refs
  - Branch name pattern enforced: `relay/issue-<int>-wip`
- `/ai <request>` parsing: request text treated as untrusted user input
  - Shell interpolation of request text is a critical injection vector
  - Pass request as argument or env var — never interpolated into shell command string
  - Length bounds enforced to prevent prompt injection via unusually long requests

## Command injection
- `subprocess` calls use list form (`["cmd", "arg"]`), never `shell=True` with dynamic input
- Any user-provided string that reaches a shell command must be validated or escaped
- `git commit -m` message sourced from controlled template, not raw user input

## Branch protection bypass
- Automation never pushes directly to `main` or `master` — enforced in code, not just policy
- Branch name validated server-side pattern before checkout/push
- Force-push (`--force`) prohibited in automation scripts

## GitHub token scope
- `GITHUB_TOKEN` used where possible — prefer over long-lived PATs
- Token not passed to Claude agent subprocess environment unless explicitly required
- Token not included in prompts sent to Claude

## Dependency security
- Third-party packages pinned to exact versions in `pyproject.toml` / lockfile
- No packages with known CVEs in the dependency graph (flag if `pip audit` or `safety` not in CI)
- GitHub Actions third-party steps pinned to full commit SHA

## Prompt injection (project-specific risk)
- Issue title and body included in Claude prompt — these are attacker-controlled
- Prompt template must wrap user content in clear delimiters
- Instructions must appear after user content, not before, to reduce override risk
- Consider truncating issue body before embedding in prompt

## Information disclosure
- Stack traces not returned to GitHub comment responses
- Internal file paths, env var names, and infrastructure details stripped before public output
- `run-log.md` persisted state files should not contain raw API responses
