# It should only contain database operations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Agent


class AgentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, agent: Agent) -> Agent:
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get(self, agent_id: UUID) -> Agent | None:
        return self.db.get(Agent, agent_id)

    def list(self) -> list[Agent]:
        stmt = select(Agent)
        return list(self.db.scalars(stmt).all())

    def update(self, agent: Agent) -> Agent:
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete(self, agent: Agent) -> None:
        self.db.delete(agent)
        self.db.commit()

    def get_by_name(self, name: str) -> Agent | None:
        stmt = select(Agent).where(Agent.name == name)
        return self.db.scalar(stmt)
