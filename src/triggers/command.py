import re
from typing import Optional, Tuple

class CommandParser:
    """Parses /ai slash commands from GitHub comments."""

    def __init__(self):
        # Matches /ai followed by any text, case-insensitive
        self.pattern = re.compile(r'^/ai\s+(.*)', re.IGNORECASE)

    def parse(self, text: str) -> Optional[str]:
        """
        Returns the command body if it matches /ai, otherwise None.
        Example: "/ai fix the bug in main.py" -> "fix the bug in main.py"
        """
        match = self.pattern.match(text)
        if match:
            return match.group(1).strip()
        return None

    def parse_confirmation(self, text: str) -> Optional[str]:
        """
        Returns 'yes' or 'no' if the comment is a valid confirmation command.
        """
        text_lower = text.strip().lower()
        if text_lower == "/ai yes":
            return "yes"
        elif text_lower == "/ai no":
            return "no"
        elif text_lower == "/ai cancel":
            return "cancel"
        return None
