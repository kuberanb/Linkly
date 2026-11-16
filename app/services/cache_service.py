
from redis.asyncio import Redis
from redis.exceptions import RedisError

import logging

logger = logging.getLogger(__name__)

async def get_cached_url(redis:Redis,code:str ) -> str | None:
    try:
       return await redis.get(f"url:{code}")
    except RedisError:
        logger.warning("Redis cache read failed; using PostgreSQL")
        return None


async def cache_url(redis:Redis, code:str,original_url:str) -> None:
    try:
        await redis.set(f"url:{code}", original_url, ex=60)

    except RedisError:
        logger.warning("Redis cache write failed; continuing without cache")
