"""
Event Consumer for the Notifications Service.
Listens to TASK_CREATED, TASK_UPDATED, USER_CREATED events and creates notifications.
Implements retry logic and Dead Letter Queue handling.
"""

import logging
import os
import sys
from typing import Dict, Any

# Add parent directory to path for importing shared_events
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from shared_events import Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


class NotificationEventConsumer:
    """Consumes events from event bus and creates notifications"""
    
    def __init__(self, db_session_factory):
        """
        Initialize the event consumer.
        
        Args:
            db_session_factory: Factory function to get database sessions
        """
        self.db_session_factory = db_session_factory
        self.event_bus = get_event_bus()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers"""
        self.event_bus.subscribe(EventType.TASK_CREATED, self._handle_task_created)
        self.event_bus.subscribe(EventType.TASK_UPDATED, self._handle_task_updated)
        self.event_bus.subscribe(EventType.USER_CREATED, self._handle_user_created)
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._handle_task_completed)
        self.event_bus.subscribe(EventType.TASK_ASSIGNED, self._handle_task_assigned)
        logger.info("✓ Event handlers registered")
    
    def _handle_task_created(self, event: Event):
        """Handle TASK_CREATED event"""
        try:
            logger.info(f"Processing TASK_CREATED event: task_id={event.aggregate_id}")
            
            task_data = event.data
            worker_ids = task_data.get("worker_ids", [])
            
            # Create notification for each assigned worker
            db = self.db_session_factory()
            try:
                from app.models.notification import Notification
                
                for worker_id in worker_ids:
                    notification = Notification(
                        user_id=worker_id,
                        task_id=int(event.aggregate_id),
                        message=f"New task assigned: {task_data.get('title')}",
                        type="task_assigned"
                    )
                    db.add(notification)
                
                db.commit()
                logger.info(f"✓ Notifications created for task: {event.aggregate_id}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"✗ Error handling TASK_CREATED event: {e}")
            raise
    
    def _handle_task_updated(self, event: Event):
        """Handle TASK_UPDATED event"""
        try:
            logger.info(f"Processing TASK_UPDATED event: task_id={event.aggregate_id}")
            
            task_data = event.data
            db = self.db_session_factory()
            try:
                from app.models.notification import Notification
                
                # Notify admins about task update
                # In production, you might want to query actual admins from auth service
                notification = Notification(
                    user_id=1,  # Default admin
                    task_id=int(event.aggregate_id),
                    message=f"Task updated: {task_data.get('title')}",
                    type="task_update"
                )
                db.add(notification)
                db.commit()
                logger.info(f"✓ Update notification created for task: {event.aggregate_id}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"✗ Error handling TASK_UPDATED event: {e}")
            raise
    
    def _handle_task_completed(self, event: Event):
        """Handle TASK_COMPLETED event"""
        try:
            logger.info(f"Processing TASK_COMPLETED event: task_id={event.aggregate_id}")
            
            event_data = event.data
            worker_id = event_data.get("worker_id")
            
            db = self.db_session_factory()
            try:
                from app.models.notification import Notification
                
                # Notify task creator about completion
                notification = Notification(
                    user_id=1,  # In real app, get from task.created_by
                    task_id=int(event.aggregate_id),
                    message=f"Task completed by worker {worker_id}",
                    type="task_completed"
                )
                db.add(notification)
                db.commit()
                logger.info(f"✓ Completion notification created for task: {event.aggregate_id}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"✗ Error handling TASK_COMPLETED event: {e}")
            raise
    
    def _handle_user_created(self, event: Event):
        """Handle USER_CREATED event"""
        try:
            logger.info(f"Processing USER_CREATED event: user_id={event.aggregate_id}")
            
            user_data = event.data
            logger.info(f"✓ New user created: {user_data.get('email')}")
            # You might want to store user info for future reference
        
        except Exception as e:
            logger.error(f"✗ Error handling USER_CREATED event: {e}")
            raise
    
    def _handle_task_assigned(self, event: Event):
        """Handle TASK_ASSIGNED event"""
        try:
            logger.info(f"Processing TASK_ASSIGNED event: task_id={event.aggregate_id}")
            
            event_data = event.data
            worker_id = event_data.get("worker_id")
            
            db = self.db_session_factory()
            try:
                from app.models.notification import Notification
                
                notification = Notification(
                    user_id=worker_id,
                    task_id=int(event.aggregate_id),
                    message=event_data.get("message", "Task assigned to you"),
                    type="task_assigned"
                )
                db.add(notification)
                db.commit()
                logger.info(f"✓ Assignment notification created for worker: {worker_id}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"✗ Error handling TASK_ASSIGNED event: {e}")
            raise
    
    def start_consuming(self, event_type: EventType = None):
        """
        Start consuming events from the event bus.
        
        Args:
            event_type: Specific event type to consume, or None for all
        """
        if event_type:
            logger.info(f"Starting event consumer for: {event_type.value}")
            self.event_bus.consume_events(event_type, consumer_group=f"notifications_{event_type.value}")
        else:
            # Consume all event types
            event_types = [
                EventType.TASK_CREATED,
                EventType.TASK_UPDATED,
                EventType.TASK_COMPLETED,
                EventType.USER_CREATED,
                EventType.TASK_ASSIGNED
            ]
            logger.info(f"Starting event consumer for all event types")
            for event_type in event_types:
                self.event_bus.consume_events(event_type, consumer_group=f"notifications_{event_type.value}")
