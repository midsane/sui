from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.types import AgentStatus


class ExecutionCreate(BaseModel):
    name: str
    description: str
    system_prompt: str
    model_id: UUID
    temperature: float = Field(ge=0.0, le=2.0)
    max_iterations: int = Field(gt=0)
    status: AgentStatus


class ExecutionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    model_id: UUID | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_iterations: int | None = Field(default=None, gt=0)
    status: AgentStatus | None = None


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    system_prompt: str
    model_id: UUID
    temperature: float
    max_iterations: int
    status: AgentStatus
    created_at: datetime
    updated_at: datetime
