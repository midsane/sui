from collections.abc import AsyncIterator
from pathlib import Path
from uuid import UUID

from app.execution.evaluation.evaluator import Evaluator
from app.execution.planning.schemas import ExecutionPlan
from app.execution.reflection.reflector import Reflector
from app.execution.tools.context import ToolContext
from app.execution.tools.registry import ToolRegistry


class Executor:
    """Executes a plan step by step with tool invocation, evaluation, and reflection."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        evaluator: Evaluator,
        reflector: Reflector,
        working_directory: Path,
    ):
        self.tool_registry = tool_registry
        self.evaluator = evaluator
        self.reflector = reflector
        self.working_directory = working_directory

    async def execute(
        self,
        plan: ExecutionPlan,
        session_id: UUID,
    ) -> AsyncIterator[str]:
        """Execute a plan step by step."""
        for step in plan.steps:
            yield f"\n📍 Step {step.index + 1}: {step.description}\n"

            tool_outputs = []
            for tool_call in step.tool_calls:
                yield f"  🔧 Calling {tool_call.tool_name}...\n"

                try:
                    context = ToolContext(
                        session_id=session_id,
                        step_index=step.index,
                        working_directory=self.working_directory,
                        tool_name=tool_call.tool_name,
                        tool_input=tool_call.parameters,
                    )
                    output = await self.tool_registry.execute(context)

                    tool_outputs.append(
                        {
                            "tool": tool_call.tool_name,
                            "output": output.output,
                            "success": output.success,
                            "error": output.error_message,
                        }
                    )

                    if output.success:
                        yield f"    ✓ {tool_call.tool_name} succeeded\n"
                    else:
                        yield f"    ✗ {tool_call.tool_name} failed: {output.error_message}\n"

                except Exception as e:
                    yield f"    ✗ Exception: {e}\n"
                    tool_outputs.append(
                        {
                            "tool": tool_call.tool_name,
                            "output": "",
                            "success": False,
                            "error": str(e),
                        }
                    )

            evaluation = await self.evaluator.evaluate(
                step_description=step.description,
                tool_outputs=tool_outputs,
                expected_outcome=step.expected_output,
            )

            if evaluation.success:
                yield f"  ✅ Step succeeded (confidence: {evaluation.confidence:.1%})\n"
            else:
                yield f"  ⚠️  Step failed: {evaluation.error_message}\n"

                if evaluation.retry_suggested:
                    yield "  🔄 Retrying step...\n"
                    reflection = await self.reflector.reflect(
                        original_step=step,
                        tool_outputs=tool_outputs,
                        error_analysis=evaluation.error_message,
                    )

                    yield f"  📝 Fix strategy: {reflection.retry_strategy}\n"
                    step = reflection.corrected_step

        yield "\n✨ All steps completed.\n"
