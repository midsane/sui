"""Define API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def home() -> dict[str, str]:
    return {"name": "Sui", "version": "0.1.0", "status": "running"}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
