from abc import ABC, abstractmethod

from app.entities.messages.models import Message


class BaseProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        history: list[Message],
    ) -> str: ...

    @abstractmethod
    async def generate_title(
        self,
        prompt: str,
    ) -> str: ...
