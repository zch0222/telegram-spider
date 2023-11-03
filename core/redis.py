from fastapi import Depends, FastAPI
import aioredis

async def get_redis():
    redis = await aioredis.create_redis_pool('redis://localhost')
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()
