from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(slots=True, frozen=True)
class ChatResult(Generic[T]):
    text: T
    usage: Usage
    model: str
    latency_ms: int


class StructuredOutputError(Exception):
    def __init__(
        self,
        response_model: type,
        raw_output: str,
        validation_error: Exception,
    ):
        self.response_model = response_model
        self.raw_output = raw_output
        self.validation_error = validation_error
        super().__init__(
            f"Failed to parse LLM output as {response_model.__name__}: "
            f"{validation_error!s}"
        )
