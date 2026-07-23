from datetime import datetime
from typing import Any
from uuid import UUID

from app.types import ExecutionStatus

from .models import Execution
from .repository import ExecutionRepository
from .schemas import ExecutionCreate


class ExecutionService:
    def __init__(self, repository: ExecutionRepository):
        self.repository = repository

    async def create_execution(self, execution: ExecutionCreate) -> Execution:
        return await self.repository.create(execution)

    async def get_execution(self, execution_id: UUID) -> Execution:
        return await self.repository.get_by_id(execution_id)

    async def list_executions(self) -> list[Execution]:
        return await self.repository.list()

    async def pause_execution(self, execution_id: UUID) -> Execution:
        return await self.repository.update_status(
            execution_id,
            ExecutionStatus.PAUSED,
        )

    async def resume_execution(self, execution_id: UUID) -> Execution:
        return await self.repository.update_status(
            execution_id,
            ExecutionStatus.RUNNING,
        )

    async def complete_execution(
        self,
        execution_id: UUID,
        result: str,
    ) -> Execution:
        return await self.repository.complete(
            execution_id=execution_id,
            result=result,
            finished_at=datetime.utcnow(),
        )

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
    ) -> Execution:
        return await self.repository.fail(
            execution_id=execution_id,
            reason=reason,
            finished_at=datetime.utcnow(),
        )

    async def append_log(
        self,
        execution_id: UUID,
        log: dict[str, Any],
    ) -> Execution:
        return await self.repository.append_log(
            execution_id,
            log,
        )

    async def update_step(
        self,
        execution_id: UUID,
        step: str,
    ) -> Execution:
        return await self.repository.update_step(
            execution_id,
            step,
        )

    async def add_token_usage(
        self,
        execution_id: UUID,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> Execution:
        return await self.repository.add_token_usage(
            execution_id,
            input_tokens,
            output_tokens,
            cost,
        )
