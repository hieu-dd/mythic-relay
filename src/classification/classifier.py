from typing import List, Optional
from .state_machine import RunStatus

class IntentClassifier:
    """Determines the type of request from the user's command."""

    def __init__(self):
        # In a real implementation, this would use an LLM.
        # For now, we use simple keyword-based classification.
        self.categories = {
            "coding": ["fix", "implement", "add", "change", "refactor", "update"],
            "research": ["explain", "find", "investigate", "how", "where"],
            "maintenance": ["update", "upgrade", "patch", "dependency"],
        }

    def classify(self, request: str) -> str:
        """
        Returns the category of the request.
        """
        request_lower = request.lower()
        for category, keywords in self.categories.items():
            if any(keyword in request_lower for keyword in keywords):
                return category
        return "coding" # Default category
