import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult, Usage
from app.types import MessageRole

from .base import BaseProvider

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Generous read budget: a long completion can be slow to finish.
TIMEOUT = httpx.Timeout(180.0, connect=10.0)

# OpenRouter attributes requests to an app via these headers.
APP_URL = "https://github.com/midsane/sui"
APP_TITLE = "Sui"

RATE_LIMIT_HINT = (
    "rate limited — ':free' models have low per-minute and daily caps. "
    "Wait a moment, or switch model/key with /providers."
)

# Upstream error bodies can be enormous; keep the tail of the message readable.
MAX_RAW_DETAIL = 300


class OpenRouterProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.api_key = api_key
        self.model = model

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": APP_URL,
            "X-Title": APP_TITLE,
        }

    def _build_messages(
        self,
        messages: list[Message],
    ) -> list[dict[str, str]]:
        payload: list[dict[str, str]] = []

        for message in messages:
            match message.role:
                case MessageRole.USER:
                    role = "user"

                case MessageRole.ASSISTANT | MessageRole.AGENT:
                    role = "assistant"

                case MessageRole.SYSTEM:
                    role = "system"

                case _:
                    # Tool output has no standalone role here without a
                    # matching tool_call_id, so fold it into the user turn.
                    role = "user"

            payload.append(
                {
                    "role": role,
                    "content": message.content,
                }
            )

        return payload

    def _body(
        self,
        messages: list[Message],
        stream: bool,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": self._build_messages(messages),
            "stream": stream,
        }

    def _raise_for_error(
        self,
        response: httpx.Response,
    ) -> None:
        """Surface OpenRouter's error message rather than a bare status code."""
        if not response.is_error:
            return

        detail = response.text
        upstream: str | None = None
        raw: str | None = None

        try:
            payload = response.json()
            error = payload.get("error")

            if isinstance(error, dict):
                detail = error.get("message", detail)

                # OpenRouter's own message is often generic ("Provider returned
                # error"); the actionable text sits in metadata.
                metadata = error.get("metadata")

                if isinstance(metadata, dict):
                    upstream = metadata.get("provider_name")
                    raw_value = metadata.get("raw")

                    if raw_value:
                        raw = str(raw_value).strip()[:MAX_RAW_DETAIL]
            elif isinstance(error, str):
                detail = error
        except (json.JSONDecodeError, AttributeError):
            pass

        parts = [f"OpenRouter request failed ({response.status_code}): {detail}"]

        if upstream:
            parts.append(f"upstream: {upstream}")

        if raw:
            parts.append(f"detail: {raw}")

        if response.status_code == 429:
            parts.append(RATE_LIMIT_HINT)

        raise RuntimeError("\n  ".join(parts))

    def _usage(
        self,
        payload: dict[str, Any],
    ) -> Usage:
        usage = payload.get("usage") or {}

        return Usage(
            input_tokens=int(usage.get("prompt_tokens", 0) or 0),
            output_tokens=int(usage.get("completion_tokens", 0) or 0),
            total_tokens=int(usage.get("total_tokens", 0) or 0),
        )

    async def llm_call(
        self,
        messages: list[Message],
    ) -> ChatResult[str]:
        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                API_URL,
                headers=self._headers(),
                json=self._body(messages, stream=False),
            )

            self._raise_for_error(response)
            payload = response.json()

        latency_ms = int((time.perf_counter() - start) * 1000)

        choices = payload.get("choices") or []

        if not choices:
            raise RuntimeError("OpenRouter returned no choices.")

        text = choices[0].get("message", {}).get("content") or ""

        return ChatResult(
            text=text,
            usage=self._usage(payload),
            model=payload.get("model") or self.model,
            latency_ms=latency_ms,
        )

    async def stream_llm_call(
        self,
        messages: list[Message],
    ) -> AsyncIterator[str]:
        async with (
            httpx.AsyncClient(timeout=TIMEOUT) as client,
            client.stream(
                "POST",
                API_URL,
                headers=self._headers(),
                json=self._body(messages, stream=True),
            ) as response,
        ):
            if response.is_error:
                # Body is unread while streaming; pull it in for the message.
                await response.aread()
                self._raise_for_error(response)

            async for line in response.aiter_lines():
                chunk = line.strip()

                # Blank lines separate events; ": ..." lines are keep-alive
                # comments OpenRouter sends while a model is warming up.
                if not chunk or chunk.startswith(":"):
                    continue

                if not chunk.startswith("data:"):
                    continue

                data = chunk[len("data:") :].strip()

                if data == "[DONE]":
                    break

                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    continue

                choices = payload.get("choices") or []

                if not choices:
                    continue

                text = choices[0].get("delta", {}).get("content")

                if text:
                    yield text
