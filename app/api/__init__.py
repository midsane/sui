from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exception import SuiError, handle_sui_error
from app.db import get_db
from app.entities.agents import router as agents_router
from app.entities.execution import router as execution_router

base_router = APIRouter()
db_dependency = Depends(get_db)


# health-check routes
@base_router.get("/")
async def home() -> dict[str, str]:
    return {"name": "Sui", "version": "0.1.0", "status": "running"}


@base_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@base_router.get("/ping-db")
async def ping_db(db: Session = db_dependency) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"db_health": "ok"}


app = FastAPI(title="Sui", version="1.0.0")


app.add_exception_handler(SuiError, handle_sui_error)
app.include_router(agents_router)
app.include_router(execution_router)
