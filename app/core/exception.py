from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.entities.agents import agent_exception


class SuiError(Exception):
    """Base class for domain errors raised by the application."""


async def handle_sui_error(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, agent_exception.AgentAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Agent with this name already exists"},
        )

    if isinstance(exc, agent_exception.AgentNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Agent not found"},
        )

    raise exc
