from abc import ABC, abstractmethod
from typing import Any

from .context import ToolContext
from .schemas import ToolOutput, ToolSchema


class ToolExecutionError(Exception):
    """Raised when a tool execution fails."""

    def __init__(self, tool_name: str, error_message: str):
        self.tool_name = tool_name
        self.error_message = error_message
        super().__init__(f"Tool '{tool_name}' failed: {error_message}")


class IToolProvider(ABC):
    """Abstract base class for tool providers."""

    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """Return the tool's schema."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        context: ToolContext,
    ) -> ToolOutput:
        """
        Execute the tool with given context.

        Args:
            context: Tool execution context

        Returns:
            ToolOutput with result

        Raises:
            ToolExecutionError: If execution fails
        """
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input against tool schema."""
        raise NotImplementedError
