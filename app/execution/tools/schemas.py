from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolPermissionLevel(Enum):
    """Permission levels for tool execution."""

    RESTRICTED = "restricted"
    NORMAL = "normal"
    FULL = "full"


@dataclass
class ToolInput:
    """Input to a tool."""

    tool_name: str
    parameters: dict[str, Any]


@dataclass
class ToolOutput:
    """Output from a tool execution."""

    tool_name: str
    success: bool
    output: str
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSchema:
    """Schema definition for a tool."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permission_level: ToolPermissionLevel = ToolPermissionLevel.NORMAL
    requires_approval: bool = False


@dataclass
class ToolInfo:
    """Public information about a tool."""

    name: str
    description: str
    permission_level: ToolPermissionLevel
    requires_approval: bool
