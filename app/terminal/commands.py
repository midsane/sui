from rich.console import Console

from app.config.schemas import Provider
from app.config.service import ConfigService
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
            case "/select":
                self.select_provider()

            case "/chats":
                await self.list_conversations()

            case "/help":
                self.help()

            case "/exit":
                raise SystemExit

            case _:
                print("Unknown command.")

    def help(self) -> None:

        print(
            """
            Commands

            /select
            /chats
            /help
            /exit
            """
        )

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

    def select_provider(self) -> None:

        print()

        print("Available Providers")
        print("1. Gemini")

        choice = input("Select: ").strip()

        if choice != "1":
            print("Invalid provider.")
            return

        api_key = input("Gemini API Key: ").strip()

        model = input("Model [gemini-2.5-pro]: ").strip()

        if model == "":
            model = "gemini-2.5-pro"

        self.config_service.configure_provider(
            provider=Provider.GEMINI,
            api_key=api_key,
            default_model=model,
        )

        print(f"✓ Gemini configured with model {model}")
