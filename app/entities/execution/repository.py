from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from schemas import ExecutionCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.types import ExecutionStatus

from .exceptions import ExecutionNotFound
from .models import Execution


class ExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, execution: ExecutionCreate) -> Execution:
        db_execution = Execution(**execution.model_dump())

        self.db.add(db_execution)
        await self.db.commit()
        await self.db.refresh(db_execution)

        return db_execution

    async def get_by_id(self, execution_id: UUID) -> Execution:
        execution = await self.db.get(Execution, execution_id)

        if execution is None:
            raise ExecutionNotFound(execution_id)

        return execution

    async def list(self) -> list[Execution]:
        result = await self.db.execute(select(Execution))
        return list(result.scalars().all())

    async def update_status(
        self,
        execution_id: UUID,
        status: ExecutionStatus,
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        execution.status = status

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def update_step(
        self,
        execution_id: UUID,
        step: str,
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        execution.current_step = step

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def append_log(
        self,
        execution_id: UUID,
        log: dict[str, Any],
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        logs = execution.logs or []
        logs.append(log)
        execution.logs = logs

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def add_token_usage(
        self,
        execution_id: UUID,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        execution.input_tokens += input_tokens
        execution.output_tokens += output_tokens
        execution.total_tokens += input_tokens + output_tokens
        execution.cost += Decimal(str(cost))

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def complete(
        self,
        execution_id: UUID,
        result: str,
        finished_at: datetime,
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        execution.status = ExecutionStatus.COMPLETED
        execution.result = result
        execution.finished_at = finished_at

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def fail(
        self,
        execution_id: UUID,
        reason: str,
        finished_at: datetime,
    ) -> Execution:
        execution = await self.get_by_id(execution_id)

        execution.status = ExecutionStatus.FAILED
        execution.result = reason
        execution.finished_at = finished_at

        await self.db.commit()
        await self.db.refresh(execution)

        return execution
