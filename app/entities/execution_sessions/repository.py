from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.types import ExecutionStatus

from .models import ExecutionSession
from .schemas import ExecutionSessionCreate, ExecutionSessionUpdate


class ExecutionSessionRepository:
    """Repository for ExecutionSession persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_create: ExecutionSessionCreate,
    ) -> ExecutionSession:
        """Create a new execution session."""
        session = ExecutionSession(
            user_id=session_create.user_id,
            task=session_create.task,
            description=session_create.description,
            metadata=session_create.metadata,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: UUID) -> ExecutionSession | None:
        """Get session by ID."""
        result = await self.db.execute(
            select(ExecutionSession).where(ExecutionSession.id == session_id)
        )
        return result.scalars().first()

    async def update(
        self,
        session_id: UUID,
        update: ExecutionSessionUpdate,
    ) -> ExecutionSession | None:
        """Update an execution session."""
        session = await self.get_by_id(session_id)
        if not session:
            return None

        if update.status is not None:
            session.status = update.status

        if update.current_step_index is not None:
            session.current_step_index = update.current_step_index

        if update.requirements is not None:
            session.requirements = update.requirements

        if update.plan is not None:
            session.plan = update.plan

        if update.outputs is not None:
            session.outputs = update.outputs

        if update.metadata is not None:
            session.metadata = update.metadata

        if update.started_at is not None:
            session.started_at = update.started_at

        if update.finished_at is not None:
            session.finished_at = update.finished_at

        if update.cancelled_at is not None:
            session.cancelled_at = update.cancelled_at

        if update.cancellation_reason is not None:
            session.cancellation_reason = update.cancellation_reason

        await self.db.flush()
        return session

    async def list_user_sessions(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExecutionSession]:
        """List sessions for a user."""
        result = await self.db.execute(
            select(ExecutionSession)
            .where(ExecutionSession.user_id == user_id)
            .order_by(ExecutionSession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def list_active_sessions(
        self,
        user_id: UUID,
    ) -> list[ExecutionSession]:
        """List active (non-completed) sessions for a user."""
        result = await self.db.execute(
            select(ExecutionSession).where(
                ExecutionSession.user_id == user_id,
                ExecutionSession.status.in_(
                    [
                        ExecutionStatus.PENDING,
                        ExecutionStatus.RUNNING,
                        ExecutionStatus.PAUSED,
                    ]
                ),
            )
        )
        return result.scalars().all()

    async def add_output(
        self,
        session_id: UUID,
        output: dict,
    ) -> ExecutionSession | None:
        """Add output to execution session."""
        session = await self.get_by_id(session_id)
        if not session:
            return None

        session.outputs.append(output)
        await self.db.flush()
        return session
