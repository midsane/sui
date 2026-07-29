from collections.abc import AsyncIterator
from typing import TypeVar

from app.config.service import ConfigService
from app.entities.messages.models import Message
from app.llms.providers.base import BaseProvider
from app.types import MessageRole

from .providers.factory import ProviderFactory
from .schemas import ChatResult

T = TypeVar("T")

TITLE_PROMPT = """
Generate a concise conversation title.

Rules:
- Maximum 5 words.
- Do not use quotation marks.
- Do not use markdown.
- Return only the title.
""".strip()


class LLMService:
    def __init__(
        self,
        config_service: ConfigService,
    ) -> None:
        self.config_service = config_service
        self._provider_instance: BaseProvider | None = None
        self._provider_fingerprint: tuple[str, str, str] | None = None

    def _provider(self) -> BaseProvider:
        entry = self.config_service.get_active_key()

        # Rebuild when the selected key, its secret, or its model changes, so
        # switching keys takes effect without restarting.
        fingerprint = (entry.provider.value, entry.api_key, entry.model)

        if (
            self._provider_instance is not None
            and self._provider_fingerprint == fingerprint
        ):
            return self._provider_instance

        self._provider_instance = ProviderFactory.create(
            provider=entry.provider,
            api_key=entry.api_key,
            model=entry.model,
        )
        self._provider_fingerprint = fingerprint

        return self._provider_instance

    async def llm_call(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        response_model: type[T] | None = None,
    ) -> ChatResult[T] | ChatResult[str]:
        history = messages

        if system_prompt is not None:
            history = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=system_prompt,
                ),
                *messages,
            ]

        if response_model is not None:
            return await self._provider().structured_llm_call(
                history,
                response_model,
            )

        return await self._provider().llm_call(history)

    def stream_llm_call(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        history = messages

        if system_prompt is not None:
            history = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=system_prompt,
                ),
                *messages,
            ]

        return self._provider().stream_llm_call(history)

    async def generate_title(
        self,
        prompt: str,
    ) -> str:
        response: ChatResult[str] = await self.llm_call(
            messages=[
                Message(
                    role=MessageRole.USER,
                    content=prompt,
                )
            ],
            system_prompt=TITLE_PROMPT,
        )

        return response.text.strip()
