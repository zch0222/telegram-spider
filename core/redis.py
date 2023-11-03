from fastapi import Depends, FastAPI
import aioredis

async def get_redis():
    redis = await aioredis.from_url("redis://localhost")
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()
