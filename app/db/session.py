from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import settings

DATABASE_URL = settings.database_url

async_engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
