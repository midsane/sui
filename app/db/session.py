# create data base engine , config and make a session to the db using engine
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.core import settings

DATABASE_URL = settings.database_url

async_engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

engine = create_engine(
    DATABASE_URL,
    # this makes sure stale connections are dropped
    pool_pre_ping=True,
    max_overflow=30,
    pool_size=20,
    pool_timeout=60,
)


def get_db() -> Generator[Session, None, None]:
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
