from dataclasses import dataclass
from uuid import UUID

from app.types import AgentStatus


@dataclass(slots=True)
class AgentCreate:
    name: str
    description: str
    system_prompt: str
    model_id: UUID
    temperature: float
    max_iterations: int
    status: AgentStatus

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")


@dataclass(slots=True)
class AgentUpdate:
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    model_id: UUID | None = None
    temperature: float | None = None
    max_iterations: int | None = None
    status: AgentStatus | None = None

    def __post_init__(self) -> None:
        if self.temperature is not None and not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        if self.max_iterations is not None and self.max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")
