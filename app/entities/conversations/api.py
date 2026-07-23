from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .models import Conversation
from .repository import ConversationRepository
from .schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from .service import ConversationService

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

db_dependency = Depends(get_db)


def get_conversation_service(
    db: AsyncSession = db_dependency,
) -> ConversationService:
    repository = ConversationRepository(db)
    return ConversationService(repository)


conversation_service_dependency = Depends(get_conversation_service)


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    conversation: ConversationCreate,
    service: ConversationService = conversation_service_dependency,
) -> Conversation:
    return await service.create_conversation(conversation)


@router.get(
    "/",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    service: ConversationService = conversation_service_dependency,
) -> list[Conversation]:
    return await service.list_conversations()


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
    conversation_id: UUID,
    service: ConversationService = conversation_service_dependency,
) -> Conversation:
    return await service.get_conversation(conversation_id)


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def update_conversation(
    conversation_id: UUID,
    conversation: ConversationUpdate,
    service: ConversationService = conversation_service_dependency,
) -> Conversation:
    return await service.update_conversation(
        conversation_id,
        conversation,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: UUID,
    service: ConversationService = conversation_service_dependency,
) -> None:
    await service.delete_conversation(conversation_id)
