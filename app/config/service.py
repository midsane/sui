import os

from .models import CONFIG_PATH, CREDENTIALS_PATH, SUI_HOME
from .schemas import (
    DEFAULT_MODELS,
    ApiKeyEntry,
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

        self._migrate_legacy()

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

        # Holds plaintext API keys, so keep it owner-only.
        os.chmod(CREDENTIALS_PATH, 0o600)

    def _migrate_legacy(self) -> None:
        """
        Fold pre-multi-key credentials into the named-key list.

        Runs once: afterwards the legacy slots are empty, so there is nothing
        left to migrate.
        """
        credentials = self.load_credentials()
        legacy = credentials.legacy_entries()

        if not legacy:
            return

        config = self.load_config()
        active_id: str | None = None

        for provider, api_key in legacy:
            is_active = provider == config.active_provider

            model = DEFAULT_MODELS[provider]
            if is_active and config.default_model is not None:
                model = config.default_model

            entry = ApiKeyEntry(
                name=provider.value,
                provider=provider,
                api_key=api_key,
                model=model,
            )
            credentials.keys.append(entry)

            if is_active:
                active_id = entry.id

        if active_id is None and credentials.keys:
            active_id = credentials.keys[0].id

        credentials.clear_legacy()
        self.save_credentials(credentials)

        config.active_key_id = active_id
        config.active_provider = None
        config.default_model = None
        self.save_config(config)

    def list_keys(self) -> list[ApiKeyEntry]:
        return self.load_credentials().keys

    def get_key(
        self,
        key_id: str,
    ) -> ApiKeyEntry | None:
        for entry in self.list_keys():
            if entry.id == key_id:
                return entry

        return None

    def get_active_key(self) -> ApiKeyEntry:
        config = self.load_config()

        if config.active_key_id is None:
            raise RuntimeError("No API key selected. Run /providers to add one.")

        entry = self.get_key(config.active_key_id)

        if entry is None:
            raise RuntimeError("Selected API key no longer exists.")

        return entry

    def has_active_provider(self) -> bool:
        config = self.load_config()

        if config.active_key_id is None:
            return False

        return self.get_key(config.active_key_id) is not None

    def add_key(
        self,
        name: str,
        provider: Provider,
        api_key: str,
        model: str,
    ) -> ApiKeyEntry:
        """Add a key, activating it if it is the first one."""
        credentials = self.load_credentials()

        if any(entry.name.lower() == name.lower() for entry in credentials.keys):
            raise ValueError(f"A key named '{name}' already exists.")

        entry = ApiKeyEntry(
            name=name,
            provider=provider,
            api_key=api_key,
            model=model,
        )
        credentials.keys.append(entry)
        self.save_credentials(credentials)

        if len(credentials.keys) == 1:
            self.set_active_key(entry.id)

        return entry

    def rename_key(
        self,
        key_id: str,
        name: str,
    ) -> ApiKeyEntry:
        credentials = self.load_credentials()

        for entry in credentials.keys:
            if entry.id != key_id and entry.name.lower() == name.lower():
                raise ValueError(f"A key named '{name}' already exists.")

        return self._update_key(credentials, key_id, name=name)

    def set_key_model(
        self,
        key_id: str,
        model: str,
    ) -> ApiKeyEntry:
        return self._update_key(self.load_credentials(), key_id, model=model)

    def set_key_secret(
        self,
        key_id: str,
        api_key: str,
    ) -> ApiKeyEntry:
        return self._update_key(self.load_credentials(), key_id, api_key=api_key)

    def _update_key(
        self,
        credentials: Credentials,
        key_id: str,
        **changes: str,
    ) -> ApiKeyEntry:
        for entry in credentials.keys:
            if entry.id != key_id:
                continue

            for field, value in changes.items():
                setattr(entry, field, value)

            self.save_credentials(credentials)
            return entry

        raise ValueError("Key not found.")

    def set_active_key(
        self,
        key_id: str,
    ) -> ApiKeyEntry:
        entry = self.get_key(key_id)

        if entry is None:
            raise ValueError("Key not found.")

        config = self.load_config()
        config.active_key_id = key_id
        self.save_config(config)

        return entry

    def remove_key(
        self,
        key_id: str,
    ) -> ApiKeyEntry:
        credentials = self.load_credentials()
        remaining = [entry for entry in credentials.keys if entry.id != key_id]

        if len(remaining) == len(credentials.keys):
            raise ValueError("Key not found.")

        removed = next(entry for entry in credentials.keys if entry.id == key_id)

        credentials.keys = remaining
        self.save_credentials(credentials)

        config = self.load_config()
        if config.active_key_id == key_id:
            config.active_key_id = remaining[0].id if remaining else None
            self.save_config(config)

        return removed
