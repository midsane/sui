from app.core.exception import SuiError


class AgentAlreadyExists(SuiError):
    """Raised when an agent with the requested name already exists."""


class AgentNotFound(SuiError):
    """Raised when an agent cannot be found."""
