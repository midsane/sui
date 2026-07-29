from typing import Any

from app.entities.messages.models import Message
from app.execution.planning.schemas import PlanStep
from app.llms.service import LLMService
from app.types import MessageRole

from .prompts import REFLECTION_PROMPT
from .schemas import ReflectionResult


class Reflector:
    """Reflects on failures and generates fixes."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def reflect(
        self,
        original_step: PlanStep,
        tool_outputs: list[dict[str, Any]],
        error_analysis: str | None = None,
    ) -> ReflectionResult:
        """
        Analyze a failed step and generate a fix.

        Args:
            original_step: The step that failed
            tool_outputs: Results from tool executions
            error_analysis: Analysis of what went wrong

        Returns:
            ReflectionResult with corrected step and fix strategy
        """
        outputs_text = "\n".join(
            [f"- {output.get('tool')}: {output.get('output')}"
             for output in tool_outputs]
        )

        prompt = f"""
Original Step: {original_step.description}

Tool Outputs:
{outputs_text}

{f'Error Analysis: {error_analysis}' if error_analysis else ''}

Analyze why this step failed and suggest a corrected version.
"""

        result = await self.llm_service.llm_call(
            messages=[
                Message(
                    role=MessageRole.USER,
                    content=prompt,
                )
            ],
            system_prompt=REFLECTION_PROMPT,
            response_model=ReflectionResult,
        )

        if isinstance(result.text, ReflectionResult):
            return result.text

        raise ValueError(
            f"Expected ReflectionResult, got {type(result.text)}"
        )
