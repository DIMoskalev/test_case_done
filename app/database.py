from datetime import datetime
from typing import Annotated, AsyncGenerator

from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.config import get_db_url

DATABASE_URL = get_db_url()

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=False)

# Создание локальной сессии для работы с базой данных
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# настройка аннотаций
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает и возвращает новую сессию базы данных."""
    async with async_session() as session:
        yield session
