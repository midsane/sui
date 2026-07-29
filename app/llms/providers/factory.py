from app.config.schemas import Provider

from .base import BaseProvider
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider

# from .openai import OpenAIProvider


class ProviderFactory:
    @staticmethod
    def supported() -> list[Provider]:
        """Providers with a working implementation behind them."""
        return [Provider.GEMINI, Provider.OPENROUTER]

    @staticmethod
    def create(
        provider: Provider,
        api_key: str,
        model: str,
    ) -> BaseProvider:
        match provider:
            case Provider.GEMINI:
                return GeminiProvider(
                    api_key=api_key,
                    model=model,
                )

            case Provider.OPENROUTER:
                return OpenRouterProvider(
                    api_key=api_key,
                    model=model,
                )

            # case Provider.OPENAI:
            #     return OpenAIProvider(
            #         api_key=api_key,
            #         model=model,
            #     )

            case _:
                raise ValueError(f"Unsupported provider: {provider}")
