# Workflow

## Purpose

Describe the GitHub Actions flow for the initial production path: `/ai <request>` on issues.

## Trigger contract

- Event: `issue_comment` (`created`)
- Guard:
  - Comment starts with `/ai`
  - Comment author is trusted collaborator/member/owner

## Request path (v0.1)

1. React with eyes
2. Create progress comment
3. Resolve item context (issue number/type)
4. Detect or create WIP branch
5. Fetch thread context
6. Parse request
7. Build prompt
8. Run Claude agent
9. Checkpoint WIP branch
10. Finalize success/failure

## Step I/O highlights

- `create-progress` outputs:
  - `progress_comment_id`
  - `progress_start_ts`
- `detect-wip` outputs:
  - `wip_branch`
  - `wip_branch_exists`
- `parse-request` outputs:
  - `user_request`
  - `model_override`
  - `max_turns_override`
- `run-agent` outputs:
  - `result`
  - `failure_reason`
  - `agent_attempts`

## Progress states

- `received`
- `planning`
- `implementing`
- `creating_pr`
- `completed`
- `failed`

## Failure path

If any stage fails:

- Update progress comment with `failed`
- Include concise `failure_reason`
- Preserve safe diagnostics for operators

## Deferred paths

- Confirmation flow (`/ai yes`, `/ai no`)
- Cancel flow (`/ai cancel`)
- Label/scheduled trigger variants
