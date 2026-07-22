# create and configure the application
from fastapi import FastAPI

from app.core.exception import AgentAlreadyExists, AgentNotFound, handle_sui_error

from .routes import router

app = FastAPI(title="Sui", version="1.0.0")

app.add_exception_handler(AgentAlreadyExists, handle_sui_error)
app.add_exception_handler(AgentNotFound, handle_sui_error)

app.include_router(router)
