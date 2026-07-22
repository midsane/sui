"""Application-specific exceptions and HTTP mappings."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class SuiError(Exception):
    """Base class for domain errors raised by the application."""


class AgentAlreadyExists(SuiError):
    """Raised when an agent with the requested name already exists."""


class AgentNotFound(SuiError):
    """Raised when an agent cannot be found."""


async def handle_sui_error(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AgentAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Agent with this name already exists"},
        )

    if isinstance(exc, AgentNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Agent not found"},
        )

    raise exc
