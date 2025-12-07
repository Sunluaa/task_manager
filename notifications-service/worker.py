"""
Background worker for processing notification queue
Run separately: python worker.py
"""
import asyncio
import logging
import logging.config
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.queue import NotificationQueue
from app.services.redis_client import RedisClient
from app.db.database import get_db, SessionLocal
from app.models.notification import Notification
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Configure logging with GMT+3 timezone
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
os.environ['TZ'] = 'Etc/GMT-3'
try:
    import time
    time.tzset()
except (AttributeError, OSError):
    # tzset is not available on Windows, but we'll try to handle it
    pass


class NotificationWorker:
    def __init__(self):
        self.db: Session = None
        self.running = False

    async def initialize(self):
        """Initialize database connection"""
        self.db = SessionLocal()
        redis_ok = await RedisClient.health_check()
        if not redis_ok:
            logger.error("Redis health check failed, retrying...")
            await asyncio.sleep(5)
            await self.initialize()
        logger.info("Worker initialized successfully")

    async def send_notification(self, payload: dict) -> bool:
        """
        Send notification - main business logic
        payload: {user_id, title, message, ...}
        """
        try:
            user_id = payload.get("user_id")
            title = payload.get("title", "Notification")
            message = payload.get("message", "")

            if not user_id:
                logger.error("user_id not found in payload")
                return False

            # Create notification in database
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                is_read=False,
            )
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)

            logger.info(f"Notification sent to user {user_id}: {title}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error sending notification: {e}")
            return False

    async def process_queue(self):
        """Main queue processing loop"""
        await self.initialize()
        self.running = True
        consecutive_errors = 0
        max_consecutive_errors = 10

        logger.info("Starting notification worker")

        try:
            while self.running:
                try:
                    # Dequeue notification
                    task_data = await NotificationQueue.dequeue_notification()

                    if not task_data:
                        # No tasks in queue, short sleep to avoid CPU spinning
                        await asyncio.sleep(1)
                        continue

                    task_id = task_data.get("task_id")
                    payload = task_data.get("payload", {})

                    logger.info(f"Processing task: {task_id}")

                    # Try to send notification
                    success = await self.send_notification(payload)

                    if success:
                        # Mark as completed
                        await NotificationQueue.mark_as_completed(task_data)
                        consecutive_errors = 0
                    else:
                        # Requeue or move to DLQ
                        will_retry = await NotificationQueue.mark_as_retry(task_data)
                        if not will_retry:
                            logger.error(f"Task moved to DLQ: {task_id}")
                        consecutive_errors = 0

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Error processing queue: {e}, consecutive errors: {consecutive_errors}")

                    if consecutive_errors >= max_consecutive_errors:
                        logger.critical("Too many consecutive errors, stopping worker")
                        self.running = False
                        break

                    await asyncio.sleep(2)

        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
        except Exception as e:
            logger.critical(f"Worker fatal error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        if self.db:
            self.db.close()
        await RedisClient.close()
        logger.info("Worker cleaned up")

    async def handle_dlq(self):
        """Monitor and handle Dead Letter Queue"""
        logger.info("Starting DLQ monitor")
        while self.running:
            try:
                dlq_items = await NotificationQueue.get_dlq_items(limit=5)
                if dlq_items:
                    logger.warning(f"Found {len(dlq_items)} items in DLQ")
                    for item in dlq_items:
                        logger.warning(f"DLQ item: {item}")
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"DLQ monitor error: {e}")
                await asyncio.sleep(10)


async def main():
    """Main entry point"""
    worker = NotificationWorker()
    
    try:
        # Run queue processing and DLQ monitoring concurrently
        await asyncio.gather(
            worker.process_queue(),
            worker.handle_dlq(),
        )
    except Exception as e:
        logger.critical(f"Fatal error in worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shutting down")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Worker startup failed: {e}")
        sys.exit(1)
