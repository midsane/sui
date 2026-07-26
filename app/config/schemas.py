from enum import StrEnum

from pydantic import BaseModel


class Provider(StrEnum):
    GEMINI = "gemini"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class ProviderCredentials(BaseModel):
    api_key: str | None = None


class Config(BaseModel):
    active_provider: Provider | None = None
    default_model: str | None = None


class Credentials(BaseModel):
    gemini: ProviderCredentials = ProviderCredentials()
    openai: ProviderCredentials = ProviderCredentials()
    openrouter: ProviderCredentials = ProviderCredentials()
