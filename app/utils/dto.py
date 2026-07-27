from dataclasses import asdict, fields
from typing import Any


def dto_to_dict(dto: Any) -> dict[str, Any]:
    """Convert a DTO dataclass into a dictionary."""
    return asdict(dto)


def update_model_from_dto(model: Any, dto: Any) -> None:
    """Update a model from a DTO, ignoring fields whose value is None."""
    for field in fields(dto):
        value = getattr(dto, field.name)

        if value is not None:
            setattr(model, field.name, value)
