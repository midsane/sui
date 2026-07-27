from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(slots=True, frozen=True)
class ChatResult:
    text: str
    usage: Usage
    model: str
    latency_ms: int
