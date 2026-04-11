from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .state_machine import RunStatus

@dataclass
class RunContext:
    """Maintains the session state across the processing pipeline."""
    run_id: str
    item_id: int
    item_type: str  # 'Issue' or 'PR'
    user_request: str
    status: RunStatus = RunStatus.RECEIVED
    backend: str = "claude-code"
    wip_branch: Optional[str] = None
    memory_branch: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None
