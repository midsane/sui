from typing import Any

from google import genai

from app.entities.messages.models import Message

from .base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
    ) -> None:
        self.client = genai.Client(
            api_key=api_key,
        )

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
    ) -> str:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self._build_contents(history),
        )

        return response.text or ""

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
