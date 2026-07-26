from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.types import MessageRole


class MessageCreate(BaseModel):
    conversation_id: UUID
    role: MessageRole
    content: str


class MessageUpdate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID

    conversation_id: UUID

    role: MessageRole

    content: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
