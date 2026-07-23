from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.types import ExecutionStatus


class ExecutionCreate(BaseModel):
    task: str
    agent_id: UUID


class ExecutionUpdate(BaseModel):
    status: ExecutionStatus | None = None
    current_step: str | None = None
    logs: str | None = None

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost: float | None = None

    result: str | None = None
    finished_at: datetime | None = None


class ExecutionResponse(BaseModel):
    id: UUID

    task: str
    agent_id: UUID

    status: ExecutionStatus

    current_step: str
    logs: str

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float

    result: str | None

    started_at: datetime
    finished_at: datetime | None

    parent_execution_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
