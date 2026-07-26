from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .models import Message
from .repository import MessageRepository
from .schemas import (
    MessageCreate,
    MessageResponse,
    MessageUpdate,
)
from .service import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)

db_dependency = Depends(get_db)


def get_message_service(
    db: AsyncSession = db_dependency,
) -> MessageService:
    repository = MessageRepository(db)
    return MessageService(repository)


message_service_dependency = Depends(get_message_service)


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    message: MessageCreate,
    service: MessageService = message_service_dependency,
) -> Message:
    return await service.create_message(message)


@router.get(
    "/",
    response_model=list[MessageResponse],
)
async def list_messages(
    service: MessageService = message_service_dependency,
) -> list[Message]:
    return await service.list_messages()


@router.get(
    "/{message_id}",
    response_model=MessageResponse,
)
async def get_message(
    message_id: UUID,
    service: MessageService = message_service_dependency,
) -> Message:
    return await service.get_message(message_id)


@router.get(
    "/conversation/{conversation_id}",
    response_model=list[MessageResponse],
)
async def list_conversation_messages(
    conversation_id: UUID,
    service: MessageService = message_service_dependency,
) -> list[Message]:
    return await service.list_conversation_messages(
        conversation_id,
    )


@router.patch(
    "/{message_id}",
    response_model=MessageResponse,
)
async def update_message(
    message_id: UUID,
    message: MessageUpdate,
    service: MessageService = message_service_dependency,
) -> Message:
    return await service.update_message(
        message_id,
        message,
    )


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message(
    message_id: UUID,
    service: MessageService = message_service_dependency,
) -> None:
    await service.delete_message(message_id)
