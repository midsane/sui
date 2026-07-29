from enum import StrEnum

from pydantic import BaseModel


class RequirementStatus(StrEnum):
    COMPLETE = "complete"
    NEEDS_INPUT = "needs_input"


class RequirementResponse(BaseModel):
    status: RequirementStatus

    reasoning: str

    question: str | None = None

    summary: str | None = None