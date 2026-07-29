from dataclasses import dataclass
from typing import Any

from app.execution.planning.schemas import PlanStep


@dataclass
class ReflectionResult:
    """Result of reflection on a failed step."""

    analysis: str
    corrected_step: PlanStep
    retry_strategy: str
    max_retries_recommended: int
    confidence: float
