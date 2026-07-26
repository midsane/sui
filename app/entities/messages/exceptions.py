from app.core.exception import SuiError


class MessageNotFound(SuiError):
    status_code = 404
    detail = "Message not found"
