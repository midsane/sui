# from fastapi import APIRouter, Depends, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.session import get_db
# from app.entities.conversations.repository import ConversationRepository
# from app.entities.conversations.service import ConversationService
# from app.entities.messages.repository import MessageRepository
# from app.entities.messages.service import MessageService
# from app.runtime.schemas import ChatRequest, ChatResponse
# from app.runtime.service import RuntimeService

# router = APIRouter(
#     prefix="/chat",
#     tags=["Chat"],
# )

# db_dependency = Depends(get_db)


# def get_runtime_service(
#     db: AsyncSession = db_dependency,
# ) -> RuntimeService:
#     conversation_service = ConversationService(
#         ConversationRepository(db)
#     )

#     message_service = MessageService(
#         MessageRepository(db)
#     )

#     return RuntimeService(
#         conversation_service=conversation_service,
#         message_service=message_service,
#     )


# runtime_service_dependency = Depends(
#     get_runtime_service
# )


# @router.post(
#     "/",
#     response_model=ChatResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def chat(
#     request: ChatRequest,
#     runtime: RuntimeService = runtime_service_dependency,
# ) -> ChatResponse:
#     return await runtime.chat(request)
