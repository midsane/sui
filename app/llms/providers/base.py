import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import is_dataclass
from typing import TypeVar

from pydantic import TypeAdapter

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult, StructuredOutputError

T = TypeVar("T")


class BaseProvider(ABC):
    @abstractmethod
    async def llm_call(
        self,
        messages: list[Message],
    ) -> ChatResult[str]:
        """Perform a single non-streaming LLM completion."""
        raise NotImplementedError

    @abstractmethod
    def stream_llm_call(
        self,
        messages: list[Message],
    ) -> AsyncIterator[str]:
        """Perform a streaming LLM completion."""
        raise NotImplementedError

    async def structured_llm_call(
        self,
        messages: list[Message],
        response_model: type[T],
    ) -> ChatResult[T]:
        """
        Perform LLM call and parse response into structured type.
        Default implementation: call llm_call and parse JSON.
        Providers should override for native structured output support.
        """
        result = await self.llm_call(messages)

        try:
            parsed_json = json.loads(result.text)
        except json.JSONDecodeError as e:
            raise StructuredOutputError(response_model, result.text, e) from e

        try:
            if is_dataclass(response_model):
                instance = response_model(**parsed_json)
            else:
                adapter = TypeAdapter(response_model)
                instance = adapter.validate_python(parsed_json)

            return ChatResult(
                text=instance,
                usage=result.usage,
                model=result.model,
                latency_ms=result.latency_ms,
            )
        except StructuredOutputError:
            raise
        except Exception as e:
            raise StructuredOutputError(response_model, result.text, e) from e
