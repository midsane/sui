from typing import ClassVar

from app.entities.execution_sessions.models import ExecutionSession
from app.types import ExecutionStatus


class ExecutionStateManager:
    """Manages state transitions for execution sessions."""

    VALID_TRANSITIONS: ClassVar[dict[ExecutionStatus, list[ExecutionStatus]]] = {
        ExecutionStatus.PENDING: [
            ExecutionStatus.RUNNING,
            ExecutionStatus.CANCELLED,
        ],
        ExecutionStatus.RUNNING: [
            ExecutionStatus.PAUSED,
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        ],
        ExecutionStatus.PAUSED: [
            ExecutionStatus.RUNNING,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.FAILED,
        ],
        ExecutionStatus.COMPLETED: [],
        ExecutionStatus.FAILED: [
            ExecutionStatus.RUNNING,
            ExecutionStatus.CANCELLED,
        ],
        ExecutionStatus.CANCELLED: [],
    }

    @staticmethod
    def is_valid_transition(
        from_status: ExecutionStatus,
        to_status: ExecutionStatus,
    ) -> bool:
        """Check if a state transition is valid."""
        if from_status not in ExecutionStateManager.VALID_TRANSITIONS:
            return False

        valid_targets = ExecutionStateManager.VALID_TRANSITIONS[from_status]
        return to_status in valid_targets

    @staticmethod
    def validate_transition(
        session: ExecutionSession,
        to_status: ExecutionStatus,
    ) -> None:
        """
        Validate a state transition.

        Raises:
            ValueError: If transition is invalid
        """
        if not ExecutionStateManager.is_valid_transition(session.status, to_status):
            raise ValueError(f"Cannot transition from {session.status} to {to_status}")

    @staticmethod
    def can_retry(session: ExecutionSession) -> bool:
        """Check if session can be retried."""
        return session.status in [ExecutionStatus.FAILED, ExecutionStatus.PAUSED]

    @staticmethod
    def can_cancel(session: ExecutionSession) -> bool:
        """Check if session can be cancelled."""
        return session.status in [
            ExecutionStatus.PENDING,
            ExecutionStatus.RUNNING,
            ExecutionStatus.PAUSED,
        ]

    @staticmethod
    def is_terminal(status: ExecutionStatus) -> bool:
        """Check if status is terminal (no further transitions possible)."""
        return status in [ExecutionStatus.COMPLETED, ExecutionStatus.CANCELLED]
