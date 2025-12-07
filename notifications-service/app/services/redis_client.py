import redis.asyncio as redis
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

class RedisClient:
    _instance: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get or create Redis client singleton"""
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            try:
                cls._instance = await redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                # Test connection
                await cls._instance.ping()
                logger.info(f"Redis connected: {redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._instance

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            logger.info("Redis connection closed")

    @classmethod
    async def health_check(cls) -> bool:
        """Check Redis health"""
        try:
            client = await cls.get_client()
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
