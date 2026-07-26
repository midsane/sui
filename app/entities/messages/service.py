from uuid import UUID

from .exceptions import MessageNotFound
from .models import Message
from .repository import MessageRepository
from .schemas import MessageCreate, MessageUpdate


class MessageService:
    def __init__(self, repository: MessageRepository):
        self.repository = repository

    async def create_message(
        self,
        message_data: MessageCreate,
    ) -> Message:
        return await self.repository.create(message_data)

    async def get_message(
        self,
        message_id: UUID,
    ) -> Message:
        message = await self.repository.get(message_id)

        if message is None:
            raise MessageNotFound(message_id)

        return message

    async def list_messages(
        self,
    ) -> list[Message]:
        return await self.repository.list()

    async def list_conversation_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        return await self.repository.list_by_conversation(
            conversation_id,
        )

    async def update_message(
        self,
        message_id: UUID,
        message_data: MessageUpdate,
    ) -> Message:
        message = await self.repository.get(message_id)

        if message is None:
            raise MessageNotFound(message_id)

        return await self.repository.update(
            message,
            message_data,
        )

    async def delete_message(
        self,
        message_id: UUID,
    ) -> None:
        message = await self.repository.get(message_id)

        if message is None:
            raise MessageNotFound(message_id)

        await self.repository.delete(message)
