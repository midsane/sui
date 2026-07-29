from collections.abc import AsyncIterator


class ExecutionService:
    async def execute(
        self,
        prompt: str,
    ) -> AsyncIterator[str]:
        yield "⚡ Execution mode detected.\n"
        yield "Execution pipeline is not implemented yet.\n"
