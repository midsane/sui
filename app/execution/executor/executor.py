class Executor:
    async def execute(
        self,
        plan: ExecutionPlan,
    ) -> AsyncIterator[str]:
        ...