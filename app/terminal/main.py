import asyncio
import time

from rich.console import Console

from app.config.service import ConfigService
from app.db import AsyncSessionLocal
from app.entities.conversations import ConversationRepository, ConversationService
from app.entities.messages import MessageRepository, MessageService
from app.llms.service import LLMService
from app.runtime.service import RuntimeService

from .commands import CommandHandler

console = Console()


async def main() -> None:
    config_service = ConfigService()

    command_handler = CommandHandler(config_service)

    async with AsyncSessionLocal() as db:
        conversation_service = ConversationService(ConversationRepository(db))

        message_service = MessageService(MessageRepository(db))

        llm_service = LLMService(config_service)

        runtime = RuntimeService(
            conversation_service,
            message_service,
            llm_service,
        )

        while True:
            console.print("[bold cyan]⚡ Sui[/bold cyan] [dim]v0.1.0[/dim]")
            prompt = console.input("[bold green]>[/bold green] ")

            if prompt.startswith("/"):
                command_handler.handle(prompt)
                continue

            start = time.perf_counter()

            status = console.status("[cyan]◉ sui Thinking...[/cyan]", spinner="dots")
            status.start()

            first_chunk = True
            async for chunk in runtime.stream_chat(prompt):
                if first_chunk:
                    status.stop()
                    console.print("[bold green]✦[/bold green] ", end="")
                    first_chunk = False

                print(chunk, end="", flush=True)

            elapsed = time.perf_counter() - start

            console.print(f"\n[dim]⏱ {elapsed:.2f}s[/dim]")


print()


if __name__ == "__main__":
    asyncio.run(main())
