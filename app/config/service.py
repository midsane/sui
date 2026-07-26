from .models import CONFIG_PATH, CREDENTIALS_PATH, SUI_HOME
from .schemas import (
    Config,
    Credentials,
    Provider,
)


class ConfigService:
    def __init__(self) -> None:
        SUI_HOME.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not CONFIG_PATH.exists():
            self.save_config(Config())

        if not CREDENTIALS_PATH.exists():
            self.save_credentials(Credentials())

    def load_config(self) -> Config:
        with CONFIG_PATH.open() as f:
            return Config.model_validate_json(f.read())

    def save_config(
        self,
        config: Config,
    ) -> None:
        with CONFIG_PATH.open("w") as f:
            f.write(
                config.model_dump_json(
                    indent=4,
                )
            )

    def load_credentials(self) -> Credentials:
        with CREDENTIALS_PATH.open() as f:
            return Credentials.model_validate_json(f.read())

    def save_credentials(
        self,
        credentials: Credentials,
    ) -> None:
        with CREDENTIALS_PATH.open("w") as f:
            f.write(
                credentials.model_dump_json(
                    indent=4,
                )
            )

    def has_active_provider(self) -> bool:
        return self.load_config().active_provider is not None

    def get_active_provider(self) -> Provider:
        config = self.load_config()

        if config.active_provider is None:
            raise RuntimeError("No provider configured.")

        return config.active_provider

    def get_api_key(
        self,
        provider: Provider,
    ) -> str:
        credentials = self.load_credentials()

        api_key = getattr(
            credentials,
            provider.value,
        ).api_key

        if api_key is None:
            raise RuntimeError(f"{provider.value} API key not configured.")

        return api_key or ""

    def configure_provider(
        self,
        provider: Provider,
        api_key: str,
        default_model: str,
    ) -> None:
        config = self.load_config()
        credentials = self.load_credentials()

        config.active_provider = provider
        config.default_model = default_model

        getattr(
            credentials,
            provider.value,
        ).api_key = api_key

        self.save_config(config)
        self.save_credentials(credentials)
