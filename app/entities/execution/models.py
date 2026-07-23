from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.types import ExecutionStatus


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus),
        default=ExecutionStatus.PENDING,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    current_step: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    logs: Mapped[list[Any]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    input_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    output_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    total_tokens: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        default=0,
        nullable=False,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    agent = relationship("Agent", back_populates="executions")
