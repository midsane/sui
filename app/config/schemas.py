from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class Provider(StrEnum):
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


DEFAULT_MODELS: dict[Provider, str] = {
    Provider.GEMINI: "gemini-2.5-pro",
    Provider.OPENAI: "gpt-4o",
    Provider.OPENROUTER: "openrouter/auto",
}


def _new_key_id() -> str:
    return uuid4().hex[:8]


def _now() -> datetime:
    return datetime.now(UTC)


class ApiKeyEntry(BaseModel):
    """A single named API key, with the model it should be used with."""

    id: str = Field(default_factory=_new_key_id)
    name: str
    provider: Provider
    api_key: str
    model: str
    created_at: datetime = Field(default_factory=_now)

    @property
    def masked_key(self) -> str:
        """Key with the middle elided, safe to display."""
        if len(self.api_key) <= 12:
            return "•" * len(self.api_key)

        return f"{self.api_key[:4]}…{self.api_key[-4:]}"


class ProviderCredentials(BaseModel):
    """Legacy single-key-per-provider slot. Retained so old files migrate."""

    api_key: str | None = None


class Credentials(BaseModel):
    keys: list[ApiKeyEntry] = Field(default_factory=list)

    gemini: ProviderCredentials = Field(default_factory=ProviderCredentials)
    openai: ProviderCredentials = Field(default_factory=ProviderCredentials)
    openrouter: ProviderCredentials = Field(default_factory=ProviderCredentials)

    def legacy_entries(self) -> list[tuple[Provider, str]]:
        """Provider/key pairs still held in the pre-multi-key layout."""
        slots = (
            (Provider.GEMINI, self.gemini),
            (Provider.OPENAI, self.openai),
            (Provider.OPENROUTER, self.openrouter),
        )

        return [
            (provider, slot.api_key)
            for provider, slot in slots
            if slot.api_key is not None and slot.api_key != ""
        ]

    def clear_legacy(self) -> None:
        self.gemini = ProviderCredentials()
        self.openai = ProviderCredentials()
        self.openrouter = ProviderCredentials()


class Config(BaseModel):
    active_key_id: str | None = None

    active_provider: Provider | None = None
    default_model: str | None = None
