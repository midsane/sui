from collections.abc import AsyncIterator

from app.config.service import ConfigService
from app.entities.messages.models import Message
from app.llms.providers.base import BaseProvider

from .providers.factory import ProviderFactory


class LLMService:
    _provider_instance: BaseProvider | None = None

    def __init__(
        self,
        config_service: ConfigService,
    ) -> None:
        self.config_service = config_service

    def _provider(self) -> BaseProvider:
        if self._provider_instance is not None:
            return self._provider_instance
        config = self.config_service.load_config()

        if config.active_provider is None:
            raise RuntimeError("No provider configured.")

        if config.default_model is None:
            raise RuntimeError("No model selected")

        self._provider_instance = ProviderFactory.create(
            provider=config.active_provider,
            api_key=self.config_service.get_api_key(
                config.active_provider,
            ),
            model=config.default_model,
        )

        return self._provider_instance

    async def chat(
        self,
        history: list[Message],
    ) -> str:
        return await self._provider().chat(history)

    def stream_chat(
        self,
        history: list[Message],
    ) -> AsyncIterator[str]:
        return self._provider().stream_chat(history)

    async def generate_title(
        self,
        prompt: str,
    ) -> str:
        return await self._provider().generate_title(prompt)
