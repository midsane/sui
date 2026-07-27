from uuid import UUID

from app.utils.dto import dto_to_dict, update_model_from_dto

from .exceptions import AgentAlreadyExists, AgentNotFound
from .models import Agent
from .repository import AgentRepository
from .schemas import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, repository: AgentRepository):
        self.repository = repository

    def create(self, data: AgentCreate) -> Agent:
        existing = self.repository.get_by_name(data.name)

        if existing:
            raise AgentAlreadyExists()

        agent = Agent(**dto_to_dict(data))

        return self.repository.create(agent)

    def get(self, agent_id: UUID) -> Agent:
        agent = self.repository.get(agent_id)

        if agent is None:
            raise AgentNotFound()

        return agent

    def agent_list(self) -> list[Agent]:
        return self.repository.list()

    def update(self, agent_id: UUID, data: AgentUpdate) -> Agent:
        agent = self.get(agent_id)

        update_model_from_dto(agent, data)

        return self.repository.update(agent)

    def delete(self, agent_id: UUID) -> None:
        agent = self.get(agent_id)
        self.repository.delete(agent)
