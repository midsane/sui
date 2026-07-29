from dataclasses import dataclass
from typing import Any

from app.types import ExecutionStatus


@dataclass(slots=True)
class PlanStep:
    description: str


@dataclass(slots=True)
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]


@dataclass
class ExecutionUpdate:
    """Update about execution progress (for streaming to terminal)."""

    status: ExecutionStatus
    message: str | None = None

    step_index: int | None = None
    step_description: str | None = None

    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_output: str | None = None

    question: str | None = None
    plan: dict[str, Any] | None = None

    progress: float | None = None
    error: str | None = None

    def format_for_terminal(self) -> str:
        """Format update as terminal output."""
        if self.message:
            return self.message

        parts = []

        if self.step_index is not None:
            parts.append(f"Step {self.step_index + 1}: {self.step_description or ''}")

        if self.tool_name:
            parts.append(f"  → Running {self.tool_name}...")

        if self.tool_output:
            parts.append(f"  ✓ {self.tool_output}")

        if self.question:
            parts.append(f"  ? {self.question}")

        if self.error:
            parts.append(f"  ✗ {self.error}")

        return "\n".join(filter(None, parts)) or self.status.value