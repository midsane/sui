from typing import Any

from .base import IToolProvider, ToolExecutionError
from .context import ToolContext
from .schemas import ToolInfo, ToolOutput, ToolPermissionLevel


class ToolRegistry:
    """Registry for tool discovery, validation, and execution."""

    def __init__(self):
        self._tools: dict[str, IToolProvider] = {}
        self._permissions: dict[str, ToolPermissionLevel] = {}

    def register(
        self,
        tool: IToolProvider,
        permission_level: ToolPermissionLevel | None = None,
    ) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: Tool provider instance
            permission_level: Override permission level (optional)
        """
        name = tool.schema.name
        self._tools[name] = tool

        if permission_level is not None:
            self._permissions[name] = permission_level
        else:
            self._permissions[name] = tool.schema.permission_level

    def get_tool(self, name: str) -> IToolProvider:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            IToolProvider instance

        Raises:
            KeyError: If tool not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def has_tool(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools

    def list_available(self) -> list[ToolInfo]:
        """List all available tools."""
        return [
            ToolInfo(
                name=tool.schema.name,
                description=tool.schema.description,
                permission_level=self._permissions[name],
                requires_approval=tool.schema.requires_approval,
            )
            for name, tool in self._tools.items()
        ]

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolOutput:
        """
        Execute a tool with permission checking.

        Args:
            context: Tool context with tool_name and parameters

        Returns:
            ToolOutput with result

        Raises:
            ToolExecutionError: If tool execution fails
            KeyError: If tool not found
        """
        tool_name = context.tool_name

        if not self.has_tool(tool_name):
            raise KeyError(f"Tool '{tool_name}' not found")

        tool = self.get_tool(tool_name)

        if not tool.validate_input(context.tool_input):
            raise ToolExecutionError(
                tool_name,
                f"Invalid input: {context.tool_input}",
            )

        try:
            return await tool.execute(context)
        except Exception as e:
            if isinstance(e, ToolExecutionError):
                raise
            raise ToolExecutionError(tool_name, str(e)) from e

    def get_permission_level(self, tool_name: str) -> ToolPermissionLevel:
        """Get permission level for a tool."""
        if tool_name not in self._permissions:
            raise KeyError(f"Tool '{tool_name}' not found")
        return self._permissions[tool_name]
