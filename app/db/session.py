"""Database session configuration."""

# create data base engine , config and make a session to the db using engine
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core import settings

DATABASE_URL = settings.database_url

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
