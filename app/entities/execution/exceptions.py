from app.core.exception import SuiError


class ExecutionNotFound(SuiError):
    status_code = 404
    detail = "Execution not found"
