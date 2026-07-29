from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A single tool invocation."""

    tool_name: str
    parameters: dict[str, Any]
    description: str = ""


@dataclass
class PlanStep:
    """A single step in an execution plan."""

    index: int
    description: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    expected_output: str = ""


@dataclass
class ExecutionPlan:
    """Complete execution plan."""

    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_duration: str = ""
    complexity: str = "medium"
