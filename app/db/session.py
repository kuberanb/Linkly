

from sqlalchemy.ext.ayncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.config import settings

# Create asynchronous database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.Debug,
    pool_pre_ping=True
)

# Create a session factory
SessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

# FastAPI database dependency
async def get_db():

    async with SessionLocal() as session:
        
        yield session