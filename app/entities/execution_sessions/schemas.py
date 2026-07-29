from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.types import ExecutionStatus


@dataclass(slots=True)
class ExecutionSessionCreate:
    user_id: UUID
    task: str
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionSessionUpdate:
    status: ExecutionStatus | None = None
    current_step_index: int | None = None
    requirements: dict[str, Any] | None = None
    plan: dict[str, Any] | None = None
    outputs: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    started_at: Any | None = None
    finished_at: Any | None = None
    cancelled_at: Any | None = None
    cancellation_reason: str | None = None


@dataclass(slots=True)
class ExecutionSessionResponse:
    id: UUID
    user_id: UUID
    task: str
    description: str | None
    status: ExecutionStatus
    requirements: dict[str, Any]
    plan: dict[str, Any] | None
    current_step_index: int
    outputs: list[dict[str, Any]]
    metadata: dict[str, Any]
    created_at: Any
    updated_at: Any
    started_at: Any | None
    finished_at: Any | None
    cancelled_at: Any | None
    cancellation_reason: str | None
