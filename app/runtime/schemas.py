from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_prompt: str
    conversation_id: UUID | None


class ChatResponse(BaseModel):
    conversation_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    reply: str
