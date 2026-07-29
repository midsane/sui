import asyncio
import shlex
from typing import Any

from .base import IToolProvider, ToolExecutionError
from .context import ToolContext
from .schemas import ToolOutput, ToolPermissionLevel, ToolSchema

TIMEOUT_SECONDS = 60
BLOCKED_COMMANDS = [
    "rm",
    "rmdir",
    "mkfs",
    "dd",
    "format",
    "deltree",
]


class BashTool(IToolProvider):
    """Tool for executing bash commands."""

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="bash",
            description="Execute bash commands in the project directory",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Bash command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default: 60)",
                        "default": 60,
                    },
                },
                "required": ["command"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "stdout": {"type": "string"},
                    "stderr": {"type": "string"},
                    "returncode": {"type": "integer"},
                },
            },
            permission_level=ToolPermissionLevel.NORMAL,
            requires_approval=False,
        )

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate bash tool input."""
        if "command" not in input_data:
            return False

        command = input_data["command"]
        if not isinstance(command, str) or not command.strip():
            return False

        return self._is_command_allowed(command)

    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is allowed."""
        try:
            parts = shlex.split(command)
            if not parts:
                return False

            base_cmd = parts[0]
            for blocked in BLOCKED_COMMANDS:
                if base_cmd.endswith(blocked):
                    return False

            return True
        except ValueError:
            return False

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolOutput:
        """Execute bash command."""
        command = context.tool_input.get("command", "").strip()
        timeout = context.tool_input.get("timeout", TIMEOUT_SECONDS)

        if not command:
            return ToolOutput(
                tool_name="bash",
                success=False,
                output="",
                error_message="Command is required",
            )

        if not self._is_command_allowed(command):
            return ToolOutput(
                tool_name="bash",
                success=False,
                output="",
                error_message=f"Command not allowed: {command}",
            )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=context.working_directory,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except TimeoutError:
                process.kill()
                return ToolOutput(
                    tool_name="bash",
                    success=False,
                    output="",
                    error_message=f"Command timeout after {timeout} seconds",
                )

            returncode = process.returncode
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            success = returncode == 0

            output = stdout_str
            if stderr_str:
                output = f"{stdout_str}\n{stderr_str}" if stdout_str else stderr_str

            return ToolOutput(
                tool_name="bash",
                success=success,
                output=output,
                error_message=None if success else f"Exit code {returncode}",
                metadata={
                    "returncode": returncode,
                    "stdout_lines": len(stdout_str.splitlines()),
                    "stderr_lines": len(stderr_str.splitlines()),
                },
            )

        except Exception as e:
            raise ToolExecutionError("bash", str(e)) from e
