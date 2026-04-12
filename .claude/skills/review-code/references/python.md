# Python Review Checklist

## Type safety (mypy)
- All function signatures have type annotations (params + return type)
- No use of `Any` without a comment explaining why
- `Optional[X]` / `X | None` used correctly — not just bare `None` returns
- TypedDict or dataclass used for structured data instead of plain dicts
- Generics used correctly (`list[str]` not `List[str]` in Python 3.10+)

## Error handling
- Exceptions caught at the right level — not swallowed silently
- `except Exception` avoided in favor of specific exception types
- Error messages are actionable — include context (e.g., which ID failed, what was expected)
- Resources (files, subprocesses, connections) closed in `finally` or via context manager (`with`)
- `subprocess` calls: always check return code; never use `shell=True` with user input

## Subprocess / process runner patterns (project-specific: MR-006)
- `subprocess.run()` used with `timeout=` argument — never unbounded
- `capture_output=True` or explicit `stdout=PIPE` to bound output
- Return code mapped to project error taxonomy: `auth_error`, `agent_timeout`, `agent_error`
- `TimeoutExpired` caught explicitly and mapped to `agent_timeout`
- Output truncated before storing/returning to prevent memory exhaustion
- No `shell=True` — use list form for args

## Code quality (ruff)
- No unused imports or variables
- No bare `except:` (catches `BaseException` including `KeyboardInterrupt`)
- No `print()` in library code — use `logging`
- Constants at module level, not magic literals inline
- Functions do one thing — flag functions with >3 responsibilities
- No mutable default arguments (`def f(x=[])` is a bug)

## CLI command surface (project-specific: MR-002)
- Each command is independently runnable (no hidden shared state)
- Outputs emitted in GitHub Actions format where applicable (`::set-output`, `echo "key=val" >> $GITHUB_OUTPUT`)
- Exit codes are meaningful: `0` = success, non-zero = failure
- `argparse` / `click` used consistently — not raw `sys.argv`

## GitHub API wrapper (project-specific: MR-003)
- API errors surfaced with actionable messages — not just re-raised raw
- Rate limit responses (429) handled with backoff or clear failure message
- Comment body sanitized before sending — no raw user input interpolated into markdown
- Pagination handled where list endpoints are used

## Testing (pytest)
- Each CLI command has at least one test
- Error paths tested, not just happy paths
- `subprocess` calls mocked in unit tests — avoid real network/git in unit tests
- Fixtures used for shared setup, not copy-paste in each test
- Test names describe the scenario: `test_run_agent_returns_auth_error_on_401`
