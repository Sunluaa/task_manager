from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import logging.config
from app.db.database import init_db
from app.controllers.notification_controller import router as notification_router
from app.services.redis_client import RedisClient

# Configure logging with GMT+3 timezone
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['default'],
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Set timezone to GMT+3
import os
os.environ['TZ'] = 'Etc/GMT-3'
try:
    import time
    time.tzset()
except (AttributeError, OSError):
    # tzset is not available on Windows, but we'll try to handle it
    pass

app = FastAPI(title="Notifications Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    try:
        await RedisClient.get_client()
        logger.info("Redis client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        # Continue startup even if Redis fails initially

@app.on_event("shutdown")
async def shutdown():
    await RedisClient.close()
    logger.info("Redis client closed")

app.include_router(notification_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "notifications-service"}

@app.get("/health/ready")
async def readiness():
    """Readiness probe - checks dependencies"""
    try:
        redis_ok = await RedisClient.health_check()
        return {
            "status": "ready" if redis_ok else "degraded",
            "service": "notifications-service",
            "redis": redis_ok
        }
    except Exception as e:
        return {
            "status": "not-ready",
            "service": "notifications-service",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
