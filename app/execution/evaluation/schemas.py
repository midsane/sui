from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Result of evaluating a step execution."""

    success: bool
    confidence: float
    evidence: str
    error_message: str | None = None
    retry_suggested: bool = False
    retry_reason: str | None = None
