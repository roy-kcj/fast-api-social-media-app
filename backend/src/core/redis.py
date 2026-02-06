import redis.asyncio as redis
from src.core.config import get_settings

redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        settings = get_settings()
        print(f"Connecting to Redis: {settings.redis_url}")
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None