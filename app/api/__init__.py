# create and configure the application
from fastapi import FastAPI

from app.core.exception import handle_sui_error
from app.entities.agents import agent_exception
from app.entities.agents import router as agents_router

app = FastAPI(title="Sui", version="1.0.0")

app.add_exception_handler(agent_exception.AgentAlreadyExists, handle_sui_error)
app.add_exception_handler(agent_exception.AgentNotFound, handle_sui_error)

app.include_router(agents_router)
