from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from .models import Execution
from .repository import ExecutionRepository
from .schemas import ExecutionCreate, ExecutionResponse
from .service import ExecutionService

router = APIRouter(prefix="/executions", tags=["Executions"])

db_dependency = Depends(get_db)


def get_execution_service(
    db: AsyncSession = db_dependency,
) -> ExecutionService:
    repository = ExecutionRepository(db)
    return ExecutionService(repository)


execution_service_dependency = Depends(get_execution_service)


@router.post(
    "/",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_execution(
    execution: ExecutionCreate,
    service: ExecutionService = execution_service_dependency,
) -> Execution:
    return await service.create_execution(execution)


@router.get("/", response_model=list[ExecutionResponse])
async def list_executions(
    service: ExecutionService = execution_service_dependency,
) -> list[Execution]:
    return await service.list_executions()


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: UUID,
    service: ExecutionService = execution_service_dependency,
) -> Execution:
    return await service.get_execution(execution_id)


@router.post("/{execution_id}/pause")
async def pause_execution(
    execution_id: UUID,
    service: ExecutionService = execution_service_dependency,
) -> Execution:
    return await service.pause_execution(execution_id)


@router.post("/{execution_id}/resume")
async def resume_execution(
    execution_id: UUID,
    service: ExecutionService = execution_service_dependency,
) -> Execution:
    return await service.resume_execution(execution_id)
