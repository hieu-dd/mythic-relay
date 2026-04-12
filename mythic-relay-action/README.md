# mythic-relay-action

Python-based GitHub Action for `mythic-relay`.

## v0 behavior

- Detect whether the current event is `issues` with `action=opened`
- Print issue number, title, and body to logs
- Expose reusable outputs for later workflow steps

## Outputs

- `is_issue_opened`: `true` or `false`
- `issue_number`
- `issue_title`
- `issue_body`

## Example usage

```yaml
name: Issue Detector

on:
  issues:
    types: [opened]

jobs:
  detect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run mythic-relay-action
        id: relay
        uses: ./mythic-relay-action

      - name: Show outputs
        run: |
          echo "is_issue_opened=${{ steps.relay.outputs.is_issue_opened }}"
          echo "issue_number=${{ steps.relay.outputs.issue_number }}"
```
