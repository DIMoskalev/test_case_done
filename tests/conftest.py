from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_test_db_url
from app.database import Base
from app.dependencies import get_session
from app.main import app

DATABASE_URL = get_test_db_url()


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_sessionmaker(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(scope="function")
def override_get_session(test_sessionmaker):
    async def _get_test_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def prepare_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def ac(
    override_get_session, prepare_database
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
