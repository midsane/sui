from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult


class BaseProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        history: list[Message],
    ) -> ChatResult: ...

    @abstractmethod
    def stream_chat(
        self,
        history: list[Message],
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def generate_title(
        self,
        prompt: str,
    ) -> str: ...
