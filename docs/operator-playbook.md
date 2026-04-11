# Operator Playbook

## Purpose

Help maintainers triage failed runs quickly.

## 5-minute triage checklist

1. Confirm trigger comment is valid `/ai ...`
2. Check progress comment exists and latest state
3. Identify failed step from workflow logs
4. Read `failure_reason`
5. Apply targeted recovery action

## Common failures and fixes

### `auth_error`
- Cause: invalid/expired model API credential
- Check: secret setup and environment mapping
- Action: rotate/update secret and rerun

### `agent_timeout`
- Cause: request too broad or model stalled
- Check: timeout config and prompt scope
- Action: narrow request; increase timeout only if justified

### `agent_error`
- Cause: runtime/CLI failure
- Check: agent command logs and CLI availability
- Action: retry after fixing environment issue

### Progress comment missing
- Cause: issue permission or API failure
- Check: workflow permissions and token scopes
- Action: grant required `issues:write` and rerun

### PR not created
- Cause: agent did not run `gh pr create` or push failed
- Check: whether prompt explicitly requested PR creation, and push logs
- Action: rerun with explicit instruction: "fix and create PR"

## Operational best practices

- Keep user requests specific and bounded
- Require explicit PR creation wording in prompt
- Preserve concise failure reasons for fast reruns
