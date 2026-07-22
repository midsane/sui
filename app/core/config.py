"""Configuration helpers."""

from pydantic_settings import BaseSettings, SettingsConfigDict

# later we will need more detailed config section for each services
# core/
# ├── config/
# │   ├── __init__.py
# │   ├── app.py              # App settings
# │   ├── database.py         # DatabaseSettings
# │   ├── llm.py              # LLMSettings
# │   ├── redis.py            # RedisSettings
# │   ├── docker.py           # DockerSettings
# │   ├── logging.py          # LoggingSettings
# │   └── settings.py         # Combines all settings into one object


class Settings(BaseSettings):
    app_name: str = "Sui"
    debug: bool = False

    database_url: str = ""
    # openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
