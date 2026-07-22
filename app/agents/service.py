from uuid import UUID

from fastapi import HTTPException

from ..schemas.agent import AgentCreate, AgentUpdate
from .models import Agent
from .repository import AgentRepository


class AgentService:
    def __init__(self, repository: AgentRepository):
        self.repository = repository

    def create(self, data: AgentCreate) -> Agent:
        existing = self.repository.get_by_name(data.name)

        if existing:
            raise HTTPException(
                status_code=409, detail="Agent with this name already exists"
            )

        agent = Agent(
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            model_id=data.model_id,
            temperature=data.temperature,
            max_iterations=data.max_iterations,
            status=data.status,
        )
        created_agent: Agent = self.repository.create(agent=agent)
        return created_agent

    def get(self, agent_id: UUID) -> Agent:
        agent = self.repository.get(agent_id)

        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")

        retrived_agent: Agent = agent
        return retrived_agent

    def agent_list(self) -> list[Agent]:
        return self.repository.list()

    def update(self, agent_id: UUID, data: AgentUpdate) -> Agent:
        agent = self.get(agent_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(agent, field, value)

        updated_agent: Agent = self.repository.update(agent)
        return updated_agent

    def delete(self, agent_id: UUID) -> None:
        agent = self.get(agent_id)
        self.repository.delete(agent)
