from enum import Enum

class RunStatus(Enum):
    RECEIVED = "received"
    CLASSIFYING = "classifying"
    RISK_ASSESSING = "risk_assessing"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    CHECKPOINTING = "checkpointing"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StateMachine:
    """Manages the legal transitions between RunStatuses."""

    _TRANSITIONS = {
        RunStatus.RECEIVED: [RunStatus.CLASSIFYING, RunStatus.FAILED],
        RunStatus.CLASSIFYING: [RunStatus.RISK_ASSESSING, RunStatus.FAILED],
        RunStatus.RISK_ASSESSING: [RunStatus.PLANNING, RunStatus.FAILED],
        RunStatus.PLANNING: [RunStatus.IMPLEMENTING, RunStatus.FAILED],
        RunStatus.IMPLEMENTING: [RunStatus.CHECKPOINTING, RunStatus.FINALIZING, RunStatus.FAILED],
        RunStatus.CHECKPOINTING: [RunStatus.IMPLEMENTING, RunStatus.FAILED],
        RunStatus.FINALIZING: [RunStatus.COMPLETED, RunStatus.FAILED],
        RunStatus.FAILED: [RunStatus.RECEIVED], # For retries
        RunStatus.COMPLETED: [],
        RunStatus.CANCELLED: [],
    }

    @classmethod
    def validate_transition(cls, current: RunStatus, next_status: RunStatus) -> bool:
        return next_status in cls._TRANSITIONS.get(current, [])
