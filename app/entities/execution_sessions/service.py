from uuid import UUID

from app.types import ExecutionStatus

from .models import ExecutionSession
from .repository import ExecutionSessionRepository
from .schemas import ExecutionSessionCreate, ExecutionSessionUpdate


class ExecutionSessionService:
    """Service for execution session management."""

    def __init__(self, repository: ExecutionSessionRepository):
        self.repository = repository

    async def create_session(
        self,
        session_create: ExecutionSessionCreate,
    ) -> ExecutionSession:
        """Create a new execution session."""
        return await self.repository.create(session_create)

    async def get_session(self, session_id: UUID) -> ExecutionSession | None:
        """Get a session by ID."""
        return await self.repository.get_by_id(session_id)

    async def update_session(
        self,
        session_id: UUID,
        update: ExecutionSessionUpdate,
    ) -> ExecutionSession | None:
        """Update a session."""
        return await self.repository.update(session_id, update)

    async def start_session(self, session_id: UUID) -> ExecutionSession | None:
        """Start a session (move to RUNNING)."""
        from datetime import datetime, timezone

        return await self.repository.update(
            session_id,
            ExecutionSessionUpdate(
                status=ExecutionStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
            ),
        )

    async def complete_session(self, session_id: UUID) -> ExecutionSession | None:
        """Complete a session."""
        from datetime import datetime, timezone

        return await self.repository.update(
            session_id,
            ExecutionSessionUpdate(
                status=ExecutionStatus.COMPLETED,
                finished_at=datetime.now(timezone.utc),
            ),
        )

    async def fail_session(
        self,
        session_id: UUID,
        error_reason: str | None = None,
    ) -> ExecutionSession | None:
        """Mark session as failed."""
        from datetime import datetime, timezone

        return await self.repository.update(
            session_id,
            ExecutionSessionUpdate(
                status=ExecutionStatus.FAILED,
                finished_at=datetime.now(timezone.utc),
                metadata={"error": error_reason} if error_reason else None,
            ),
        )

    async def cancel_session(
        self,
        session_id: UUID,
        reason: str | None = None,
    ) -> ExecutionSession | None:
        """Cancel a session."""
        from datetime import datetime, timezone

        return await self.repository.update(
            session_id,
            ExecutionSessionUpdate(
                status=ExecutionStatus.CANCELLED,
                cancelled_at=datetime.now(timezone.utc),
                cancellation_reason=reason,
            ),
        )

    async def add_output(
        self,
        session_id: UUID,
        output: dict,
    ) -> ExecutionSession | None:
        """Add output to a session."""
        return await self.repository.add_output(session_id, output)

    async def list_user_sessions(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExecutionSession]:
        """List sessions for a user."""
        return await self.repository.list_user_sessions(user_id, limit, offset)

    async def get_active_sessions(
        self,
        user_id: UUID,
    ) -> list[ExecutionSession]:
        """Get active sessions for a user."""
        return await self.repository.list_active_sessions(user_id)
