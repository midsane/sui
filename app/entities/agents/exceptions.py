from app.core.exception import SuiError


class AgentAlreadyExists(SuiError):
    status_code = 409

    detail = "Agent already exists"


class AgentNotFound(SuiError):
    status_code = 404

    detail = "Agent not found"
