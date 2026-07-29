from rich.console import Console
from rich.markup import escape
from rich.table import Table

from app.config.schemas import DEFAULT_MODELS, ApiKeyEntry, Provider
from app.config.service import ConfigService
from app.llms.providers.factory import ProviderFactory
from app.runtime.service import RuntimeService

console = Console()


class CommandHandler:
    def __init__(self, config_service: ConfigService, runtime_service: RuntimeService):
        self.config_service = config_service
        self.runtime_service = runtime_service
        self.selecting_chat = False

    async def handle(
        self,
        command: str,
    ) -> None:

        match command.strip():
            case "/providers" | "/keys" | "/select":
                self.manage_keys()

            case "/chats":
                await self.list_conversations()

            case "/help":
                self.help()

            case "/exit":
                raise SystemExit

            case _:
                print("Unknown command.")

    def help(self) -> None:
        table = Table(box=None, pad_edge=False, show_header=False)
        table.add_column(style="bold cyan")
        table.add_column(style="dim")

        table.add_row("/providers", "manage API keys and models")
        table.add_row("/chats", "browse conversation history")
        table.add_row("/help", "show this help")
        table.add_row("/exit", "quit")

        console.print("\n[bold]Commands[/bold]\n")
        console.print(table)
        console.print()

    async def list_conversations(self) -> None:
        conversations = await self.runtime_service.list_conversations()

        if not conversations:
            print("No conversations found.")
            return

        print("\nChat History\n")

        for i, conv in enumerate(conversations, start=1):
            print(f"{i}. {conv.title}")

        print("\nn. new chat")
        print("\nq. Cancel")

        choice = input("\nSelect: ").strip()

        if choice.lower() == "n":
            self.runtime_service.active_conversation_id = None
            return

        if choice.lower() == "q":
            return

        try:
            index = int(choice) - 1
        except ValueError:
            print("Invalid selection.")
            return

        if not (0 <= index < len(conversations)):
            print("Invalid selection.")
            return

        conversation = conversations[index]

        await self.runtime_service.set_active_conversation(conversation.id)

        messages = await self.runtime_service.get_conversation_messages(
            conversation.id,
        )
        console.clear()

        print(f"\n✓ Switched to '{conversation.title}'\n")

        # Render messages here (or call your renderer)
        for message in messages:
            print(f"{message.role}: {message.content}")

    def manage_keys(self) -> None:
        """Interactive manager for named API keys."""
        while True:
            keys = self.config_service.list_keys()
            self._render_keys(keys)

            if not keys:
                console.print(
                    "  [dim]No API keys yet. Press[/dim] [bold cyan]a[/bold cyan] "
                    "[dim]to add one.[/dim]\n"
                )

            console.print(
                "  [bold cyan]a[/bold cyan] [dim]add[/dim]    "
                "[bold cyan]u[/bold cyan] [dim]use[/dim]    "
                "[bold cyan]m[/bold cyan] [dim]model[/dim]    "
                "[bold cyan]n[/bold cyan] [dim]rename[/dim]    "
                "[bold cyan]k[/bold cyan] [dim]replace key[/dim]    "
                "[bold cyan]d[/bold cyan] [dim]delete[/dim]    "
                "[bold cyan]q[/bold cyan] [dim]back[/dim]"
            )

            choice = console.input("\n[bold green]>[/bold green] ").strip().lower()

            try:
                match choice:
                    case "a":
                        self._add_key()
                    case "u":
                        self._use_key(keys)
                    case "m":
                        self._edit_model(keys)
                    case "n":
                        self._rename_key(keys)
                    case "k":
                        self._replace_secret(keys)
                    case "d":
                        self._delete_key(keys)
                    case "q" | "":
                        return
                    case _:
                        console.print("[red]Unknown option.[/red]")
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

    def _render_keys(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        console.print("\n[bold]API Keys[/bold]\n")

        if not keys:
            return

        active_id = self.config_service.load_config().active_key_id

        table = Table(box=None, pad_edge=False, header_style="dim")
        table.add_column("", width=2)
        table.add_column("#", width=3, style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Provider")
        table.add_column("Model")
        table.add_column("Key", style="dim")

        for index, entry in enumerate(keys, start=1):
            is_active = entry.id == active_id

            table.add_row(
                "[green]●[/green]" if is_active else "",
                str(index),
                f"[green]{entry.name}[/green]" if is_active else entry.name,
                entry.provider.value,
                entry.model,
                entry.masked_key,
            )

        console.print(table)
        console.print()

    def _ask(
        self,
        label: str,
        default: str | None = None,
    ) -> str:
        """Prompt with an optional default hint, escaped so rich shows brackets."""
        hint = f" [{default}]" if default is not None else ""

        return console.input(f"[dim]{escape(label + hint)}: [/dim]").strip()

    def _pick_key(
        self,
        keys: list[ApiKeyEntry],
        action: str,
    ) -> ApiKeyEntry | None:
        if not keys:
            console.print("[red]No keys to choose from.[/red]")
            return None

        raw = self._ask(f"{action} which #?")

        if raw == "" or raw.lower() == "q":
            return None

        try:
            index = int(raw) - 1
        except ValueError:
            console.print("[red]Enter a number from the list.[/red]")
            return None

        if not (0 <= index < len(keys)):
            console.print("[red]No key with that number.[/red]")
            return None

        return keys[index]

    def _add_key(self) -> None:
        providers = ProviderFactory.supported()

        console.print()
        for index, provider in enumerate(providers, start=1):
            console.print(f"  [bold cyan]{index}[/bold cyan] {provider.value}")

        if len(providers) == 1:
            provider = providers[0]
        else:
            raw = self._ask("Provider #")

            try:
                provider = providers[int(raw) - 1]
            except (ValueError, IndexError):
                console.print("[red]Invalid provider.[/red]")
                return

        api_key = self._ask(f"{provider.value} API key")

        if api_key == "":
            console.print("[red]API key cannot be empty.[/red]")
            return

        default_model = DEFAULT_MODELS[provider]
        model = self._ask("Model", default_model)
        model = model or default_model

        default_name = self._default_name(provider)
        name = self._ask("Name", default_name)
        name = name or default_name

        entry = self.config_service.add_key(
            name=name,
            provider=provider,
            api_key=api_key,
            model=model,
        )

        console.print(f"[green]✓[/green] Added '{entry.name}' ({entry.model})")

    def _default_name(
        self,
        provider: Provider,
    ) -> str:
        existing = {entry.name.lower() for entry in self.config_service.list_keys()}

        if provider.value not in existing:
            return provider.value

        suffix = 2
        while f"{provider.value}-{suffix}" in existing:
            suffix += 1

        return f"{provider.value}-{suffix}"

    def _use_key(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        entry = self._pick_key(keys, "Use")

        if entry is None:
            return

        self.config_service.set_active_key(entry.id)
        console.print(f"[green]✓[/green] Now using '{entry.name}' ({entry.model})")

    def _edit_model(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        entry = self._pick_key(keys, "Edit model for")

        if entry is None:
            return

        model = self._ask("Model", entry.model)

        if model == "" or model == entry.model:
            return

        self.config_service.set_key_model(entry.id, model)
        console.print(f"[green]✓[/green] '{entry.name}' now uses {model}")

    def _rename_key(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        entry = self._pick_key(keys, "Rename")

        if entry is None:
            return

        name = self._ask("Name", entry.name)

        if name == "" or name == entry.name:
            return

        self.config_service.rename_key(entry.id, name)
        console.print(f"[green]✓[/green] Renamed to '{name}'")

    def _replace_secret(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        entry = self._pick_key(keys, "Replace key for")

        if entry is None:
            return

        api_key = self._ask("New API key")

        if api_key == "":
            return

        self.config_service.set_key_secret(entry.id, api_key)
        console.print(f"[green]✓[/green] Updated key for '{entry.name}'")

    def _delete_key(
        self,
        keys: list[ApiKeyEntry],
    ) -> None:
        entry = self._pick_key(keys, "Delete")

        if entry is None:
            return

        confirm = self._ask(f"Delete '{entry.name}'? [y/N]").lower()

        if confirm != "y":
            return

        self.config_service.remove_key(entry.id)
        console.print(f"[green]✓[/green] Deleted '{entry.name}'")

        if not self.config_service.has_active_provider():
            console.print("[yellow]No key is active. Add or select one.[/yellow]")
