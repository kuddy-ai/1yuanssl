"""Pytest fixtures for backend API tests."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Import models so SQLAlchemy metadata is fully populated for create_all.
from app import models  # noqa: F401
from app.db import Base, get_db
from app.main import app


@pytest_asyncio.fixture
async def client(tmp_path) -> AsyncGenerator[AsyncClient, None]:
    """Create an API client backed by an isolated temporary SQLite database."""
    database_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    engine = create_async_engine(database_url, poolclass=NullPool)
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as api_client:
        yield api_client

    app.dependency_overrides.clear()
    await engine.dispose()
