from contextlib import asynccontextmanager
from typing import Annotated, List

import uvicorn
from fastapi import Depends, FastAPI, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, engine
from app.dependencies import get_session
from app.funcs import get_filtered_posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/posts/")
async def fetch_posts(
    category: str | None = None,
    keywords: Annotated[List[str] | None, Query()] = None,
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await get_filtered_posts(session, category, keywords, limit, offset)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
