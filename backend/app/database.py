"""SQLAlchemy async engine, session maker, and Base declarative model.

Provides the async database engine, session factory, and dependency
for injecting database sessions into FastAPI route handlers.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Create async engine with connection pool settings optimized for remote & serverless PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=5,
    pool_recycle=300,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args={"timeout": 5},
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency that provides an async database session.

    Yields an async session and ensures it is closed after the request.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
