import json
import os
import sys
import uuid


def set_output(name: str, value: str) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return

    delimiter = f"MYTHIC_RELAY_{uuid.uuid4().hex}"
    with open(output_path, "a", encoding="utf-8") as output_file:
        output_file.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def load_event_payload() -> dict:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("GITHUB_EVENT_PATH is not set", file=sys.stderr)
        return {}

    try:
        with open(event_path, "r", encoding="utf-8") as event_file:
            return json.load(event_file)
    except FileNotFoundError:
        print(f"Event payload file not found: {event_path}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in event payload: {exc}", file=sys.stderr)
        return {}


def main() -> int:
    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    payload = load_event_payload()
    action = payload.get("action", "")
    issue = payload.get("issue") or {}

    is_issue_opened = event_name == "issues" and action == "opened"
    is_pr_opened = event_name == "pull_request" and action == "opened"

    issue_number = str(issue.get("number", ""))
    issue_title = str(issue.get("title", ""))
    issue_body = issue.get("body") or ""

    set_output("is_issue_opened", "true" if is_issue_opened else "false")
    set_output("issue_number", issue_number)
    set_output("issue_title", issue_title)
    set_output("issue_body", issue_body)

    print("[mythic-relay-action] event inspection")
    print(f"[mythic-relay-action] GITHUB_EVENT_NAME={event_name}")
    print(f"[mythic-relay-action] action={action}")

    if is_pr_opened:
        print("Trigger when open PR")
        return 0

    if not is_issue_opened:
        print("[mythic-relay-action] skip: not an issue opened event")
        return 0

    print(f"[mythic-relay-action] issue_number={issue_number}")
    print(f"[mythic-relay-action] issue_title={issue_title}")
    print("[mythic-relay-action] issue_body:")
    print(issue_body if issue_body else "(empty)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
