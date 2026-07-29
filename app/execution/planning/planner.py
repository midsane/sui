from app.entities.messages.models import Message
from app.llms.service import LLMService
from app.types import MessageRole

from .prompts import PLANNER_PROMPT
from .schemas import ExecutionPlan, PlanStep, ToolCall


class Planner:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    async def plan(
        self,
        requirements: str,
        tools_available: list[str] | None = None,
    ) -> ExecutionPlan:
        """
        Generate an execution plan from requirements.

        Args:
            requirements: Task description with context
            tools_available: List of available tool names

        Returns:
            ExecutionPlan with steps and tool calls
        """
        tools_info = ""
        if tools_available:
            tools_info = f"\n\nAvailable tools: {', '.join(tools_available)}"

        prompt = f"""
Requirements:
{requirements}
{tools_info}

Generate an execution plan to accomplish this task.
"""

        result = await self.llm_service.llm_call(
            messages=[
                Message(
                    role=MessageRole.USER,
                    content=prompt,
                )
            ],
            system_prompt=PLANNER_PROMPT,
            response_model=ExecutionPlan,
        )

        if isinstance(result.text, ExecutionPlan):
            return result.text

        raise ValueError(f"Expected ExecutionPlan, got {type(result.text)}")