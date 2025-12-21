"""
Event Consumer Worker for Notifications Service.
Runs as a separate service/process to consume events from the event bus.
"""

import logging
import os
import sys

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add shared_events to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.services.event_consumer import NotificationEventConsumer
from shared_events import EventType


def start_event_consumer():
    """Start the event consumer service"""
    logger.info("=" * 60)
    logger.info("Starting Notification Event Consumer")
    logger.info("=" * 60)
    
    try:
        consumer = NotificationEventConsumer(db_session_factory=SessionLocal)
        
        logger.info("✓ Event consumer initialized")
        logger.info("Listening for events...")
        logger.info("")
        
        # Start consuming events
        # This will block and consume events indefinitely
        consumer.event_bus.consume_events(
            event_type=EventType.TASK_CREATED,
            consumer_group="notifications_service"
        )
    
    except KeyboardInterrupt:
        logger.info("Event consumer stopped by user")
    except Exception as e:
        logger.error(f"✗ Event consumer error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    start_event_consumer()
