import json
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import is_dataclass
from typing import Any, TypeVar, cast

from pydantic import TypeAdapter

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult, StructuredOutputError

T = TypeVar("T")

_FENCE_RE = re.compile(
    r"```(?:json|JSON)?\s*(?P<body>.*?)\s*```",
    re.DOTALL,
)


def _decode_json(text: str) -> Any:
    """
    Parse JSON from raw LLM output.

    Models frequently wrap JSON in markdown fences or surround it with prose
    despite being told not to, so fall back to fence extraction and then to
    the outermost brace/bracket span before giving up.
    """
    candidates = [text.strip()]

    fence = _FENCE_RE.search(text)
    if fence is not None:
        candidates.append(fence.group("body").strip())

    for opening, closing in (("{", "}"), ("[", "]")):
        start = text.find(opening)
        end = text.rfind(closing)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1].strip())

    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            last_error = e

    raise last_error or json.JSONDecodeError("No JSON found in output", text, 0)


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
            parsed_json = _decode_json(result.text)
        except json.JSONDecodeError as e:
            raise StructuredOutputError(response_model, result.text, e) from e

        try:
            instance: T
            if is_dataclass(response_model):
                # is_dataclass narrows to type[DataclassInstance], losing T.
                instance = cast("T", response_model(**parsed_json))
            else:
                adapter: TypeAdapter[T] = TypeAdapter(response_model)
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
