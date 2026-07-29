from collections.abc import AsyncIterator
from pathlib import Path
from uuid import UUID, uuid4

from app.entities.execution_sessions.schemas import (
    ExecutionSessionCreate,
    ExecutionSessionUpdate,
)
from app.entities.execution_sessions.service import ExecutionSessionService
from app.entities.messages.models import Message
from app.execution.evaluation.evaluator import Evaluator
from app.execution.executor.executor import Executor
from app.execution.planning.planner import Planner
from app.execution.reflection.reflector import Reflector
from app.execution.requirements.agent import RequirementAgent
from app.execution.requirements.schemas import RequirementStatus
from app.execution.tools.registry import ToolRegistry
from app.llms.schemas import StructuredOutputError
from app.llms.service import LLMService
from app.types import ExecutionStatus, MessageRole


class ExecutionService:
    def __init__(
        self,
        llm_service: LLMService,
        tool_registry: ToolRegistry,
        session_service: ExecutionSessionService,
        working_directory: Path | None = None,
    ):
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.session_service = session_service
        self.working_directory = working_directory or Path.cwd()

        self.requirement_agent = RequirementAgent(llm_service)
        self.planner = Planner(llm_service)
        evaluator = Evaluator(llm_service)
        reflector = Reflector(llm_service)

        self.executor = Executor(
            tool_registry=tool_registry,
            evaluator=evaluator,
            reflector=reflector,
            working_directory=self.working_directory,
        )

    async def execute(
        self,
        prompt: str,
        user_id: UUID | None = None,
    ) -> AsyncIterator[str]:
        """
        Execute a user prompt end-to-end.

        Orchestrates: requirement gathering → planning → execution → evaluation.
        """
        if user_id is None:
            user_id = uuid4()

        session = None
        try:
            yield "🚀 Starting execution...\n"

            session = await self.session_service.create_session(
                ExecutionSessionCreate(
                    user_id=user_id,
                    task=prompt,
                )
            )

            yield "📋 Gathering requirements...\n"

            try:
                requirements_result = await self.requirement_agent.gather(
                    [Message(role=MessageRole.USER, content=prompt)]
                )
            except StructuredOutputError as e:
                yield f"⚠️  Could not parse requirements from LLM. Raw output: {e.raw_output}\n"
                yield "Proceeding with full prompt as requirements...\n"
                requirements_result = None

            if requirements_result is None:
                pass
            elif requirements_result.status == RequirementStatus.NEEDS_INPUT:
                yield f"❓ {requirements_result.question}\n"
                return
            else:
                yield f"✓ Requirements: {requirements_result.summary}\n"

            yield "🤖 Creating execution plan...\n"
            available_tools = [
                tool.name for tool in self.tool_registry.list_available()
            ]
            requirements_text = prompt
            if requirements_result is not None and requirements_result.summary:
                requirements_text = requirements_result.summary

            plan = await self.planner.plan(
                requirements_text,
                tools_available=available_tools,
            )

            yield f"📊 Plan created: {len(plan.steps)} steps\n"
            for step in plan.steps:
                yield f"  {step.index + 1}. {step.description}\n"

            await self.session_service.update_session(
                session.id,
                ExecutionSessionUpdate(status=ExecutionStatus.RUNNING),
            )

            yield "\n⚙️  Executing plan...\n"
            async for chunk in self.executor.execute(
                plan=plan,
                session_id=session.id,
            ):
                yield chunk

            await self.session_service.complete_session(session.id)
            yield "\n✅ Execution completed successfully.\n"

        except Exception as e:
            if session is not None:
                await self.session_service.fail_session(session.id, str(e))
            yield f"\n❌ Execution failed: {e}\n"
