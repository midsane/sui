from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.types import ExecutionStatus


@dataclass(slots=True)
class ExecutionCreate:
    task: str
    agent_id: UUID


@dataclass(slots=True)
class ExecutionUpdate:
    status: ExecutionStatus | None = None
    current_step: str | None = None
    logs: str | None = None

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost: float | None = None

    result: str | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in ("input_tokens", "output_tokens", "total_tokens"):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise ValueError(f"{field_name} cannot be negative")

        if self.estimated_cost is not None and self.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative")
