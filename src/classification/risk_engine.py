from typing import Dict, Any, Tuple
from .state_machine import RunStatus

class RiskEngine:
    """Evaluates risk signals to determine if a request needs confirmation."""

    def __init__(self):
        # Keywords that trigger a high-risk assessment
        self.risky_keywords = {
            "delete", "remove", "drop", "truncate", "rm -rf",
            "chmod", "chown", "password", "secret", "token",
            "auth", "security", "api-key", "credentials"
        }

    def evaluate(self, request: str, category: str) -> Tuple[bool, str]:
        """
        Evaluates the risk of a request.
        Returns (needs_confirmation, risk_tier).
        """
        request_lower = request.lower()

        # Check for high-risk keywords
        for keyword in self.risky_keywords:
            if keyword in request_lower:
                return True, "high"

        # Category-based risk
        if category == "maintenance":
            # Maintenance often involves dependency updates, which can be risky
            return True, "medium"

        if category == "coding":
            # General coding is typically auto-runnable unless high-risk keywords match
            return False, "low"

        return False, "low"
