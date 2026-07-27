from collections.abc import AsyncIterator
from uuid import UUID

from app.entities.conversations import (
    Conversation,
    ConversationService,
    conversation_schemas,
)
from app.entities.messages import Message, MessageService, messages_schemas
from app.llms.service import LLMService
from app.types import MessageRole

from .schemas import ChatResponse


class RuntimeService:
    def __init__(
        self,
        conversation_service: ConversationService,
        message_service: MessageService,
        llm_service: LLMService,
    ):
        self.conversation_service = conversation_service
        self.message_service = message_service
        self.llm_service = llm_service
        self.active_conversation_id: UUID | None = None

    async def list_conversations(self) -> list[Conversation]:
        return await self.conversation_service.list_conversations()

    async def get_conversations_messages(
        self, selected_conversation_id: UUID
    ) -> list[Message]:
        return await self.message_service.list_conversation_messages(
            selected_conversation_id
        )

    async def set_active_conversation(self, conversation_id: UUID) -> None:
        self.active_conversation_id = conversation_id

    async def chat(self, prompt: str) -> ChatResponse:

        if self.active_conversation_id is None:
            title = await self.llm_service.generate_title(prompt)
            conv_title = conversation_schemas.ConversationCreate(title=title)
            conversation = await self.conversation_service.create_conversation(
                conv_title
            )
            # now get this conversation id
            self.active_conversation_id = conversation.id

        # now add user message in this conversation
        user_message = await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=prompt,
                role=MessageRole.USER,
            )
        )

        history = await self.message_service.list_conversation_messages(
            self.active_conversation_id
        )

        # now call the llm with this user message
        # and give some kind of system prompt to llm to figure out if user is asking something
        # that will require tool access like making a project, getting todays weather etc

        chat_result = await self.llm_service.chat(history)

        reply = chat_result.text

        assistant_message = await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=reply,
                role=MessageRole.ASSISTANT,
            )
        )

        return ChatResponse(
            conversation_id=self.active_conversation_id,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
            reply=assistant_message.content,
            usage=chat_result.usage,
            model=chat_result.model,
            latency_ms=chat_result.latency_ms,
        )

    async def stream_chat(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:
        if self.active_conversation_id is None:
            title = await self.llm_service.generate_title(prompt)

            conversation = await self.conversation_service.create_conversation(
                conversation_schemas.ConversationCreate(
                    title=title,
                )
            )

            self.active_conversation_id = conversation.id

        user_message = await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=prompt,
                role=MessageRole.USER,
            )
        )

        history = await self.message_service.list_conversation_messages(
            self.active_conversation_id
        )

        reply = ""

        async for chunk in self.llm_service.stream_chat(history):
            reply += chunk
            yield chunk

        assistant_message = await self.message_service.create_message(
            messages_schemas.MessageCreate(
                conversation_id=self.active_conversation_id,
                content=reply,
                role=MessageRole.ASSISTANT,
            )
        )

        _ = user_message
        _ = assistant_message
