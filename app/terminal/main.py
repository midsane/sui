import asyncio
import time
from pathlib import Path

from rich.console import Console

from app.config.service import ConfigService
from app.db import AsyncSessionLocal
from app.entities.conversations import ConversationRepository, ConversationService
from app.entities.execution_sessions import (
    ExecutionSessionRepository,
    ExecutionSessionService,
)
from app.entities.messages import MessageRepository, MessageService
from app.execution.service import ExecutionService
from app.execution.tools import ToolRegistry
from app.execution.tools.bash_tool import BashTool
from app.execution.tools.file_tool import FileTool
from app.execution.tools.http_tool import HttpTool
from app.llms.service import LLMService
from app.runtime.intent import IntentRouter
from app.runtime.service import RuntimeService

from .commands import CommandHandler

console = Console()


async def run() -> None:
    config_service = ConfigService()

    async with AsyncSessionLocal() as db:
        conversation_service = ConversationService(ConversationRepository(db))

        message_service = MessageService(MessageRepository(db))

        llm_service = LLMService(config_service)

        intent_router = IntentRouter(llm_service)

        tool_registry = ToolRegistry()
        tool_registry.register(FileTool())
        tool_registry.register(BashTool())
        tool_registry.register(HttpTool())

        session_service = ExecutionSessionService(ExecutionSessionRepository(db))

        execution_service = ExecutionService(
            llm_service=llm_service,
            tool_registry=tool_registry,
            session_service=session_service,
            working_directory=Path.cwd(),
        )

        runtime = RuntimeService(
            conversation_service=conversation_service,
            message_service=message_service,
            llm_service=llm_service,
            execution_service=execution_service,
            intent_router=intent_router,
        )

        command_handler = CommandHandler(config_service, runtime_service=runtime)

        while True:
            console.print("[bold cyan]⚡ Sui[/bold cyan] [dim]v0.1.0[/dim]")
            prompt = console.input("[bold green]>[/bold green] ")

            if prompt.startswith("/"):
                await command_handler.handle(prompt)
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


def main() -> None:
    asyncio.run(run())
