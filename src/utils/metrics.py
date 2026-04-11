from dataclasses import dataclass
from typing import Optional

@dataclass
class RunMetrics:
    """Tracks reliability and autonomy outcomes."""
    run_id: str
    duration: float
    confirmation_count: int
    retry_count: int
    failure_reason: Optional[str] = None
    success: bool = False

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "duration": self.duration,
            "confirmation_count": self.confirmation_count,
            "retry_count": self.retry_count,
            "failure_reason": self.failure_reason,
            "success": self.success
        }
