# create and configure the application
from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Sui", version="1.0.0")

app.include_router(router)
