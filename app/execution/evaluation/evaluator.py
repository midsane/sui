from typing import Any

from app.entities.messages.models import Message
from app.llms.service import LLMService
from app.types import MessageRole

from .prompts import EVALUATION_PROMPT
from .schemas import EvaluationResult


class Evaluator:
    """Evaluates whether a step succeeded."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def evaluate(
        self,
        step_description: str,
        tool_outputs: list[dict[str, Any]],
        expected_outcome: str | None = None,
    ) -> EvaluationResult:
        """
        Evaluate if a step succeeded based on outputs.

        Args:
            step_description: What the step was supposed to do
            tool_outputs: Results from tool executions
            expected_outcome: What success looks like

        Returns:
            EvaluationResult with success/failure assessment
        """
        outputs_text = "\n".join(
            [
                f"- {output.get('tool')}: {output.get('output')}"
                for output in tool_outputs
            ]
        )

        prompt = f"""
Step: {step_description}

Tool Outputs:
{outputs_text}

{f"Expected: {expected_outcome}" if expected_outcome else ""}

Evaluate whether this step succeeded.
"""

        result = await self.llm_service.llm_call(
            messages=[
                Message(
                    role=MessageRole.USER,
                    content=prompt,
                )
            ],
            system_prompt=EVALUATION_PROMPT,
            response_model=EvaluationResult,
        )

        if isinstance(result.text, EvaluationResult):
            return result.text

        raise ValueError(f"Expected EvaluationResult, got {type(result.text)}")
