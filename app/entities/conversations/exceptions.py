from app.core.exception import SuiError


class ConversationNotFound(SuiError):
    status_code = 404
    detail = "Conversation not found"
