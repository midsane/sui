from uuid import UUID

from pydantic import BaseModel

from app.llms.schemas import Usage


class ChatResponse(BaseModel):
    conversation_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID

    reply: str

    usage: Usage
    model: str
    latency_ms: int
