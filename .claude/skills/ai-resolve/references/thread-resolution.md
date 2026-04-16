# Thread Resolution — GitHub MCP Patterns

## Fetch PR Details

Use `githubGet` or equivalent MCP tool:
```
Tool: github_get_repo
Args: owner, repo
```

For PR-specific details:
```
Tool: github_get_pull_request
Args: owner, repo, pull_number
```

## Fetch Review Threads

```
Tool: github_list_pull_request_comments
Args: owner, repo, pull_number
```

Returns threaded review comments. Each comment has:
- `id`: comment ID
- `body`: text content
- `path`: file path (for diff comments)
- `line`: line number (for diff comments)
- `commit_id`: the commit the comment refers to
- `threadId` or `in_reply_to_id`: thread grouping

## Resolve a Thread

```
Tool: github_create_pull_request_review_comment
Args: owner, repo, pull_number, body, commit_id, path, line
```

For resolving (marking as resolved):
```
Tool: github_update_pull_request_review_comment
Args: owner, repo, comment_id, body, state (resolved/dismissed)
```

Note: GitHub's API distinguishes between:
- **Review comments** (on the diff) — can be resolved via `PUT /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/threads`
- **Issue comments** — cannot be "resolved" programmatically, only replied to

## Reply to a Thread

```
Tool: github_create_pull_request_review_comment
Args: owner, repo, pull_number, body, in_reply_to_id
```

The `in_reply_to_id` links the reply to an existing thread.

## Post PR Summary Comment

Use the issue-comment or PR comment API:
```
Tool: github_create_issue_comment
Args: owner, repo, issue_number, body
```

Or for PR-level comments via the PR review API:
```
Tool: github_create_pull_request_review
Args: owner, repo, pull_number, body, event (COMMENT/APPROVE/REQUEST_CHANGES)
```

## Comment Body Sanitization

- Never interpolate raw user input (from review comments) directly into markdown
- Truncate long comment bodies before processing
- Strip HTML/markdown injection attempts
- Use structured formatting for counts and lists

## Rate Limit Handling

- On 429: wait 1 second, retry once
- On 403: fail fast — insufficient permissions
- Log all API calls with redacted bodies

## Submit GitHub Review

Use `github_create_pull_request_review` to submit a review:

```
Tool: github_create_pull_request_review
Args: owner, repo, pull_number, body, event (APPROVE/REQUEST_CHANGES/COMMENT)
```

- **APPROVE** — when all actionable threads are resolved or replied
- **REQUEST_CHANGES** — when unresolved actionable threads remain
- **COMMENT** — for informational-only reviews (no action on PR state)

## MCP Fallback

If GitHub MCP is unavailable or all retries fail:
1. Produce a ready-to-paste comment body in the same format as the summary would have been
2. Clearly report the MCP blocker in the final output
3. Do not silently skip posting — always surface the result