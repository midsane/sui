import time
from collections.abc import AsyncIterator
from typing import Any

from google import genai

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult, Usage
from app.types import MessageRole

from .base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _build_contents(
        self,
        messages: list[Message],
    ) -> list[dict[str, Any]]:
        contents: list[dict[str, Any]] = []

        for message in messages:
            match message.role:
                case MessageRole.USER:
                    role = "user"

                case MessageRole.ASSISTANT:
                    role = "model"

                case MessageRole.SYSTEM:
                    # Gemini doesn't support a separate "system" role
                    # so we send it as a user message.
                    role = "user"

                case _:
                    role = "user"

            contents.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": message.content,
                        }
                    ],
                }
            )

        return contents

    async def llm_call(
        self,
        messages: list[Message],
    ) -> ChatResult[str]:
        start = time.perf_counter()

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self._build_contents(messages),
        )

        latency_ms = int((time.perf_counter() - start) * 1000)

        usage_metadata = response.usage_metadata

        usage = Usage(
            input_tokens=int(
                getattr(
                    usage_metadata,
                    "prompt_token_count",
                    0,
                )
                or 0
            ),
            output_tokens=int(
                getattr(
                    usage_metadata,
                    "candidates_token_count",
                    0,
                )
                or 0
            ),
            total_tokens=int(
                getattr(
                    usage_metadata,
                    "total_token_count",
                    0,
                )
                or 0
            ),
        )

        return ChatResult(
            text=response.text or "",
            usage=usage,
            model=self.model,
            latency_ms=latency_ms,
        )

    async def stream_llm_call(
        self,
        messages: list[Message],
    ) -> AsyncIterator[str]:
        stream: Any = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=self._build_contents(messages),
        )

        async for chunk in stream:
            text = chunk.text or ""

            if text:
                yield text
