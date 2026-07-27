import time
from collections.abc import AsyncIterator
from typing import Any

from google import genai

from app.entities.messages.models import Message
from app.llms.schemas import ChatResult, Usage

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
        history: list[Message],
    ) -> list[dict[str, Any]]:
        contents = []

        for message in history:
            role = "model" if message.role.value.lower() == "assistant" else "user"

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

    async def chat(
        self,
        history: list[Message],
    ) -> ChatResult:
        start = time.perf_counter()

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self._build_contents(history),
        )

        latency_ms = int((time.perf_counter() - start) * 1000)

        usage_metadata = response.usage_metadata

        usage = Usage(
            input_tokens=int(getattr(usage_metadata, "prompt_token_count", 0) or 0),
            output_tokens=int(
                getattr(usage_metadata, "candidates_token_count", 0) or 0
            ),
            total_tokens=int(getattr(usage_metadata, "total_token_count", 0) or 0),
        )

        return ChatResult(
            text=response.text or "",
            usage=usage,
            model=self.model,
            latency_ms=latency_ms,
        )

    async def stream_chat(
        self,
        history: list[Message],
    ) -> AsyncIterator[str]:
        stream: Any = await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=self._build_contents(history),
        )

        async for chunk in stream:
            text = chunk.text or ""

            if text:
                yield text

    async def generate_title(
        self,
        prompt: str,
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=(
                "Generate a concise conversation title "
                "(maximum 5 words).\n\n"
                f"User prompt: {prompt}"
            ),
        )

        return (response.text or "").strip()
