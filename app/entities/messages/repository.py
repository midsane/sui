import builtins
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.dto import dto_to_dict, update_model_from_dto

from .models import Message
from .schemas import MessageCreate, MessageUpdate


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        message_data: MessageCreate,
    ) -> Message:
        message = Message(**dto_to_dict(message_data))

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get(
        self,
        message_id: UUID,
    ) -> Message | None:
        return await self.db.get(Message, message_id)

    async def list(
        self,
    ) -> builtins.list[Message]:
        result = await self.db.execute(
            select(Message).order_by(Message.created_at.asc())
        )

        return list(result.scalars().all())

    async def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> builtins.list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        message: Message,
        message_data: MessageUpdate,
    ) -> Message:
        update_model_from_dto(message, message_data)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def delete(
        self,
        message: Message,
    ) -> None:
        await self.db.delete(message)
        await self.db.commit()
