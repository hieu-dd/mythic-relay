from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseAgent(ABC):
    """Abstract base class for all coding agent backends."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def execute_task(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the coding task and returns the result.

        Returns:
            A dictionary containing:
            - 'success': bool
            - 'output': str (the agent's output/logs)
            - 'changes': List[str] (list of modified files)
            - 'error': Optional[str]
        """
        pass

    @abstractmethod
    def cancel(self, run_id: str) -> bool:
        """Cancels an ongoing agent run."""
        pass
