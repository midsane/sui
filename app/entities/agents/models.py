from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...db import Base
from ...types import AgentStatus


class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    llm_id: Mapped[UUID] = mapped_column(ForeignKey("llms.id"), nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False)
    max_iterations: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    executions = relationship(
        "Execution", back_populates="agent", cascade="all, delete-orphan"
    )
