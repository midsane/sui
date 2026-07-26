from app.config.schemas import Provider
from app.config.service import ConfigService


class CommandHandler:
    def __init__(
        self,
        config_service: ConfigService,
    ):
        self.config_service = config_service

    def handle(
        self,
        command: str,
    ) -> None:

        match command.strip():
            case "/select":
                self.select_provider()

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
            /help
            /exit
            """
        )

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
