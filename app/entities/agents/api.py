from uuid import UUID

from fastapi import APIRouter, Depends
from schemas import AgentCreate, AgentResponse, AgentUpdate
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

from .models import Agent
from .repository import AgentRepository
from .service import AgentService

router = APIRouter()

# dependencies
db_dependency = Depends(get_db)


def get_agent_repository(db: Session = db_dependency) -> AgentRepository:
    return AgentRepository(db)


agent_repository_dependency = Depends(get_agent_repository)


def get_agent_service(
    repo: AgentRepository = agent_repository_dependency,
) -> AgentService:
    return AgentService(repo)


agent_service_dependency = Depends(get_agent_service)


# health-check routes
@router.get("/")
async def home() -> dict[str, str]:
    return {"name": "Sui", "version": "0.1.0", "status": "running"}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ping-db")
async def ping_db(db: Session = db_dependency) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"db_health": "ok"}


# Agent Routes
@router.get("/agent/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: UUID, service: AgentService = agent_service_dependency
) -> Agent:
    return service.get(agent_id)


@router.post("/agent/create", response_model=AgentResponse)
def create_agent(
    agent_data: AgentCreate, service: AgentService = agent_service_dependency
) -> Agent:
    return service.create(agent_data)


@router.patch("/agent/update/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    service: AgentService = agent_service_dependency,
) -> Agent:
    return service.update(agent_id, agent_data)


@router.get("/agents", response_model=AgentResponse)
def list_agent(service: AgentService = agent_service_dependency) -> list[Agent]:
    return service.agent_list()


@router.delete("/agent/delete/{agent_id}")
def delete_agent(
    agent_id: UUID, service: AgentService = agent_service_dependency
) -> str:

    service.delete(agent_id)
    return f"successfully deleted agent with id:{agent_id}"
