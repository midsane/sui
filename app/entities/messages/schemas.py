from dataclasses import dataclass
from uuid import UUID

from app.types import MessageRole


@dataclass(slots=True)
class MessageCreate:
    conversation_id: UUID
    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("content cannot be empty")


@dataclass(slots=True)
class MessageUpdate:
    content: str

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("content cannot be empty")
