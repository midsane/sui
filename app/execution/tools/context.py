from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import UUID


@dataclass
class ToolContext:
    """Context for a single tool call."""

    session_id: UUID
    step_index: int
    working_directory: Path
    tool_name: str
    tool_input: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Context for entire execution session."""

    session_id: UUID
    user_id: UUID
    working_directory: Path
    project_root: Path
    current_step: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
