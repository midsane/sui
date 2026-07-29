from app.entities.messages.models import Message
from app.llms.service import LLMService

from .prompts import REQUIREMENT_PROMPT
from .schemas import RequirementResponse


class RequirementAgent:
    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:
        self.llm_service = llm_service

    async def gather(
        self,
        history: list[Message],
    ) -> RequirementResponse:
        """
        Gather requirements from conversation history.

        Returns:
            RequirementResponse with status and optional question/summary
        """
        result = await self.llm_service.llm_call(
            messages=history,
            system_prompt=REQUIREMENT_PROMPT,
            response_model=RequirementResponse,
        )

        if isinstance(result.text, RequirementResponse):
            return result.text

        raise ValueError(f"Expected RequirementResponse, got {type(result.text)}")
