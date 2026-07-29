from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult


class BaseProvider(ABC):
    @abstractmethod
    async def llm_call(
        self,
        messages: list[Message],
    ) -> ChatResult:
        """Perform a single non-streaming LLM completion."""
        raise NotImplementedError

    @abstractmethod
    def stream_llm_call(
        self,
        messages: list[Message],
    ) -> AsyncIterator[str]:
        """Perform a streaming LLM completion."""
        raise NotImplementedError
