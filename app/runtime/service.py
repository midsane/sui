from collections.abc import AsyncIterator
from uuid import UUID

from app.entities.conversations import (
    Conversation,
    ConversationService,
    conversation_schemas,
)
from app.entities.messages import (
    Message,
    MessageService,
    messages_schemas,
)
from app.execution.service import ExecutionService
from app.llms.service import LLMService
from app.types import MessageRole

from .intent import IntentRouter
from .schemas import ChatResponse, Intent


class RuntimeService:
    def __init__(
        self,
        conversation_service: ConversationService,
        message_service: MessageService,
        llm_service: LLMService,
        execution_service: ExecutionService,
        intent_router: IntentRouter,
    ) -> None:
        self.conversation_service = conversation_service
        self.message_service = message_service
        self.llm_service = llm_service
        self.execution_service = execution_service
        self.intent_router = intent_router

        self.active_conversation_id: UUID | None = None

    async def list_conversations(
        self,
    ) -> list[Conversation]:
        return await self.conversation_service.list_conversations()

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        return await self.message_service.list_conversation_messages(
            conversation_id,
        )

    async def set_active_conversation(
        self,
        conversation_id: UUID,
    ) -> None:
        self.active_conversation_id = conversation_id

    async def chat(
        self,
        prompt: str,
    ) -> ChatResponse:
        history = await self._prepare_chat(prompt)

        result = await self.llm_service.llm_call(history)
        if self.active_conversation_id is None:
            raise RuntimeError("Invalid conversation id")

        assistant_message = await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=result.text,
                role=MessageRole.ASSISTANT,
            )
        )

        return ChatResponse(
            conversation_id=self.active_conversation_id,
            user_message_id=history[-1].id,
            assistant_message_id=assistant_message.id,
            reply=assistant_message.content,
            usage=result.usage,
            model=result.model,
            latency_ms=result.latency_ms,
        )

    async def stream_chat(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:
        history = await self._prepare_chat(prompt)

        intent = await self.intent_router.classify(history)
        if self.active_conversation_id is None:
            raise RuntimeError("Invalid conversation id")

        match intent:
            case Intent.CHAT:
                reply = ""

                async for chunk in self.llm_service.stream_llm_call(history):
                    reply += chunk
                    yield chunk

                await self.message_service.create_message(
                    messages_schemas.MessageCreate(
                        conversation_id=self.active_conversation_id,
                        content=reply,
                        role=MessageRole.ASSISTANT,
                    )
                )

            case Intent.EXECUTE:
                async for chunk in self.execution_service.execute(prompt):
                    yield chunk

    async def _prepare_chat(
        self,
        prompt: str,
    ) -> list[Message]:
        await self._ensure_active_conversation(prompt)

        await self._create_user_message(prompt)

        if self.active_conversation_id is None:
            raise RuntimeError("No active conversation.")

        return await self.message_service.list_conversation_messages(
            self.active_conversation_id,
        )

    async def _ensure_active_conversation(
        self,
        prompt: str,
    ) -> None:
        if self.active_conversation_id is not None:
            return

        title = await self.llm_service.generate_title(prompt)

        conversation = await self.conversation_service.create_conversation(
            conversation_schemas.ConversationCreate(
                title=title,
            )
        )

        self.active_conversation_id = conversation.id

    async def _create_user_message(
        self,
        prompt: str,
    ) -> Message:
        if self.active_conversation_id is None:
            raise RuntimeError("No active conversation.")

        return await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=prompt,
                role=MessageRole.USER,
            )
        )
