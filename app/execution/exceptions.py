class ExecutionError(Exception):
    pass


class PlanningError(ExecutionError):
    pass


class ExecutorError(ExecutionError):
    pass
