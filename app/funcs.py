import re
from collections import Counter
from typing import Dict, List

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post

WORD_RE = re.compile(r"\w+")


async def get_filtered_posts(
    session: AsyncSession,
    category: str | None = None,
    keywords: List[str] | None = None,
    limit: int = 10,
    offset: int = 0,
) -> Dict:
    query = select(Post)

    if category:
        query = query.where(Post.category == category)
    if keywords:
        filters = [Post.content.ilike(f"%{kw}%") for kw in keywords]
        query = query.where(or_(*filters))

    total_count = await session.scalar(
        select(func.count()).select_from(query.subquery())
    )

    query = query.offset(offset).limit(limit)

    stream = await session.stream_scalars(query)

    results = []
    async for post in stream:
        words = WORD_RE.findall(post.content.lower())
        freq = dict(Counter(words))
        results.append({"id": post.id, "category": post.category, "word_freq": freq})

    return {"total": total_count, "items": results}
