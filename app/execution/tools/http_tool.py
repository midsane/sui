from typing import Any

from .base import IToolProvider, ToolExecutionError
from .context import ToolContext
from .schemas import ToolOutput, ToolPermissionLevel, ToolSchema

TIMEOUT_SECONDS = 30


class HttpTool(IToolProvider):
    """Tool for making HTTP requests."""

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="http",
            description="Make HTTP requests (GET, POST, PUT, DELETE)",
            input_schema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method",
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to request",
                    },
                    "headers": {
                        "type": "object",
                        "description": "Optional HTTP headers",
                    },
                    "body": {
                        "type": "string",
                        "description": "Request body (for POST/PUT)",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30)",
                        "default": 30,
                    },
                },
                "required": ["method", "url"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status_code": {"type": "integer"},
                    "body": {"type": "string"},
                    "headers": {"type": "object"},
                },
            },
            permission_level=ToolPermissionLevel.NORMAL,
            requires_approval=False,
        )

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate HTTP tool input."""
        if "method" not in input_data or "url" not in input_data:
            return False

        method = input_data["method"]
        url = input_data["url"]

        if method not in ["GET", "POST", "PUT", "DELETE"]:
            return False

        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return False

        return True

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolOutput:
        """Execute HTTP request."""
        try:
            import aiohttp
        except ImportError:
            return ToolOutput(
                tool_name="http",
                success=False,
                output="",
                error_message="aiohttp not installed. Install with: pip install aiohttp",
            )

        method = context.tool_input.get("method", "GET").upper()
        url = context.tool_input.get("url", "")
        headers = context.tool_input.get("headers", {})
        body = context.tool_input.get("body")
        timeout = context.tool_input.get("timeout", TIMEOUT_SECONDS)

        if not url:
            return ToolOutput(
                tool_name="http",
                success=False,
                output="",
                error_message="URL is required",
            )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    data=body,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    response_text = await response.text()
                    response_headers = dict(response.headers)

                    success = 200 <= response.status < 300

                    return ToolOutput(
                        tool_name="http",
                        success=success,
                        output=response_text,
                        error_message=None if success else f"HTTP {response.status}",
                        metadata={
                            "status_code": response.status,
                            "headers": response_headers,
                            "content_length": len(response_text),
                        },
                    )

        except TimeoutError:
            return ToolOutput(
                tool_name="http",
                success=False,
                output="",
                error_message=f"Request timeout after {timeout} seconds",
            )
        except Exception as e:
            raise ToolExecutionError("http", str(e)) from e
