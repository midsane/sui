from uuid import UUID

from .exceptions import ConversationNotFound
from .models import Conversation
from .repository import ConversationRepository
from .schemas import ConversationCreate, ConversationUpdate


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    async def create_conversation(
        self,
        conversation_data: ConversationCreate,
    ) -> Conversation:
        return await self.repository.create(conversation_data)

    async def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation:
        conversation = await self.repository.get(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        return conversation

    async def list_conversations(
        self,
    ) -> list[Conversation]:
        return await self.repository.list()

    async def update_conversation(
        self,
        conversation_id: UUID,
        conversation_data: ConversationUpdate,
    ) -> Conversation:
        conversation = await self.repository.get(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        return await self.repository.update(
            conversation,
            conversation_data,
        )

    async def delete_conversation(
        self,
        conversation_id: UUID,
    ) -> None:
        conversation = await self.repository.get(conversation_id)

        if conversation is None:
            raise ConversationNotFound(conversation_id)

        await self.repository.delete(conversation)
