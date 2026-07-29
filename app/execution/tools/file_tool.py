import os
from pathlib import Path
from typing import Any

from .base import IToolProvider, ToolExecutionError
from .context import ToolContext
from .schemas import ToolOutput, ToolPermissionLevel, ToolSchema


class FileTool(IToolProvider):
    """Tool for file operations: read, write, list."""

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="file",
            description="Read, write, or list files in the project directory",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "write", "list", "exists"],
                        "description": "File operation to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "File path relative to project root",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (only for write action)",
                    },
                },
                "required": ["action", "path"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "files": {"type": "array", "items": {"type": "string"}},
                },
            },
            permission_level=ToolPermissionLevel.NORMAL,
            requires_approval=False,
        )

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate file tool input."""
        if "action" not in input_data or "path" not in input_data:
            return False

        action = input_data["action"]
        if action not in ["read", "write", "list", "exists"]:
            return False

        if action == "write" and "content" not in input_data:
            return False

        return True

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolOutput:
        """Execute file operation."""
        action = context.tool_input.get("action")
        path_str = context.tool_input.get("path")

        if not path_str:
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message="Path is required",
            )

        path = context.working_directory / path_str

        try:
            if action == "read":
                return self._read_file(path)
            elif action == "write":
                content = context.tool_input.get("content", "")
                return self._write_file(path, content)
            elif action == "list":
                return self._list_files(path)
            elif action == "exists":
                return self._check_exists(path)
            else:
                return ToolOutput(
                    tool_name="file",
                    success=False,
                    output="",
                    error_message=f"Unknown action: {action}",
                )
        except Exception as e:
            raise ToolExecutionError("file", str(e))

    def _read_file(self, path: Path) -> ToolOutput:
        """Read file contents."""
        if not path.exists():
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"File not found: {path}",
            )

        if not path.is_file():
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"Not a file: {path}",
            )

        try:
            content = path.read_text(encoding="utf-8")
            return ToolOutput(
                tool_name="file",
                success=True,
                output=content,
                metadata={"lines": len(content.splitlines())},
            )
        except Exception as e:
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"Failed to read file: {e}",
            )

    def _write_file(self, path: Path, content: str) -> ToolOutput:
        """Write content to file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

            return ToolOutput(
                tool_name="file",
                success=True,
                output=f"Wrote {len(content)} bytes to {path}",
                metadata={
                    "file": str(path),
                    "bytes": len(content),
                    "lines": len(content.splitlines()),
                },
            )
        except Exception as e:
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"Failed to write file: {e}",
            )

    def _list_files(self, path: Path) -> ToolOutput:
        """List files in directory."""
        if not path.exists():
            path = path.parent

        if not path.is_dir():
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"Not a directory: {path}",
            )

        try:
            files = []
            for item in sorted(path.iterdir()):
                relative_path = str(item.relative_to(path.parent.parent))
                if item.is_dir():
                    files.append(f"{relative_path}/")
                else:
                    files.append(relative_path)

            output = "\n".join(files)
            return ToolOutput(
                tool_name="file",
                success=True,
                output=output,
                metadata={"count": len(files)},
            )
        except Exception as e:
            return ToolOutput(
                tool_name="file",
                success=False,
                output="",
                error_message=f"Failed to list files: {e}",
            )

    def _check_exists(self, path: Path) -> ToolOutput:
        """Check if file exists."""
        exists = path.exists()
        output = f"File {'exists' if exists else 'does not exist'}: {path}"

        return ToolOutput(
            tool_name="file",
            success=True,
            output=output,
            metadata={"exists": exists, "is_file": path.is_file() if exists else False},
        )
