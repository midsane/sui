import asyncio

from app.config.service import ConfigService
from app.db import AsyncSessionLocal
from app.entities.conversations import ConversationRepository, ConversationService
from app.entities.messages import MessageRepository, MessageService
from app.llms.service import LLMService
from app.runtime.service import RuntimeService

from .commands import CommandHandler


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
            prompt = input("> ")

            if prompt.startswith("/"):
                command_handler.handle(prompt)

                continue

            response = await runtime.chat(prompt)

            print(response.reply)


if __name__ == "__main__":
    asyncio.run(main())
