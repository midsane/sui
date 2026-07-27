from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.dto import dto_to_dict, update_model_from_dto

from .models import Conversation
from .schemas import ConversationCreate, ConversationUpdate


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_data: ConversationCreate,
    ) -> Conversation:
        conversation = Conversation(**dto_to_dict(conversation_data))

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        return await self.db.get(Conversation, conversation_id)

    async def list(
        self,
    ) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        conversation: Conversation,
        conversation_data: ConversationUpdate,
    ) -> Conversation:
        update_model_from_dto(conversation, conversation_data)

        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def delete(
        self,
        conversation: Conversation,
    ) -> None:
        await self.db.delete(conversation)
        await self.db.commit()
