"""
Event Bus for asynchronous communication between microservices.
Uses Redis Streams for event publishing and consumption.
Supports retries and Dead Letter Queue (DLQ).
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for inter-service communication"""
    # Auth events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_ASSIGNED = "task.assigned"
    TASK_COMPLETED = "task.completed"
    
    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"


@dataclass
class Event:
    """Base event class"""
    event_type: EventType
    aggregate_id: str  # ID of the entity that triggered the event
    aggregate_type: str  # Entity type (user, task, etc.)
    data: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(
            event_type=EventType(data["event_type"]),
            aggregate_id=data["aggregate_id"],
            aggregate_type=data["aggregate_type"],
            data=data.get("data", {}),
            timestamp=data.get("timestamp")
        )


class EventBus:
    """Redis Streams-based event bus for publish-subscribe pattern"""
    
    def __init__(self, redis_url: str = None):
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.max_retries = 3
        self.dlq_stream = "event_dlq"
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"✓ Event Bus connected to Redis: {redis_url}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Redis: {e}")
            raise
    
    def publish(self, event: Event) -> str:
        """
        Publish event to the event bus.
        Returns event ID.
        """
        stream_key = f"events:{event.event_type.value}"
        
        event_data = {
            "type": event.event_type.value,
            "aggregate_id": event.aggregate_id,
            "aggregate_type": event.aggregate_type,
            "data": json.dumps(event.data),
            "timestamp": event.timestamp,
            "retries": "0"
        }
        
        try:
            event_id = self.redis_client.xadd(stream_key, event_data)
            logger.info(f"✓ Event published: {event.event_type.value} (ID: {event_id})")
            return event_id
        except Exception as e:
            logger.error(f"✗ Failed to publish event: {e}")
            raise
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to a specific event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"✓ Handler subscribed to: {event_type.value}")
    
    def consume_events(self, event_type: EventType, consumer_group: str, batch_size: int = 10):
        """
        Consume events from stream.
        Implements retry logic and sends to DLQ on failure.
        
        Args:
            event_type: Type of events to consume
            consumer_group: Consumer group name (for tracking consumption)
            batch_size: Number of events to process at once
        """
        stream_key = f"events:{event_type.value}"
        
        # Create consumer group if it doesn't exist
        try:
            self.redis_client.xgroup_create(stream_key, consumer_group, id="0", mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        
        consumer_name = f"{consumer_group}_worker"
        
        while True:
            try:
                # Read pending messages first
                messages = self.redis_client.xreadgroup(
                    groupname=consumer_group,
                    consumername=consumer_name,
                    streams={stream_key: ">"},
                    count=batch_size,
                    block=1000  # Block for 1 second
                )
                
                if messages:
                    for stream, event_messages in messages:
                        for msg_id, msg_data in event_messages:
                            try:
                                self._process_event(msg_data, stream_key, consumer_group, msg_id)
                                # Acknowledge successful processing
                                self.redis_client.xack(stream, consumer_group, msg_id)
                                logger.info(f"✓ Event processed: {msg_id}")
                            except Exception as e:
                                self._handle_event_failure(msg_data, msg_id, stream_key, consumer_group, str(e))
            
            except KeyboardInterrupt:
                logger.info("Event consumer stopped")
                break
            except Exception as e:
                logger.error(f"✗ Error consuming events: {e}")
    
    def _process_event(self, msg_data: Dict[str, str], stream_key: str, consumer_group: str, msg_id: str):
        """Process a single event"""
        event_type = EventType(msg_data["type"])
        event = Event(
            event_type=event_type,
            aggregate_id=msg_data["aggregate_id"],
            aggregate_type=msg_data["aggregate_type"],
            data=json.loads(msg_data["data"]),
            timestamp=msg_data["timestamp"]
        )
        
        # Call registered handlers
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(event)
        else:
            logger.warning(f"No handlers registered for event type: {event_type.value}")
    
    def _handle_event_failure(self, msg_data: Dict[str, str], msg_id: str, stream_key: str, consumer_group: str, error: str):
        """Handle event processing failure with retry logic"""
        retries = int(msg_data.get("retries", 0))
        
        if retries < self.max_retries:
            # Retry: update retries count and re-add to stream
            retries += 1
            msg_data["retries"] = str(retries)
            new_id = self.redis_client.xadd(stream_key, msg_data)
            logger.warning(f"⚠ Event retry {retries}/{self.max_retries}: {msg_id} → {new_id}. Error: {error}")
            
            # Acknowledge original message
            self.redis_client.xack(stream_key, consumer_group, msg_id)
        else:
            # Max retries exceeded - send to DLQ
            dlq_data = {
                **msg_data,
                "original_id": msg_id,
                "error": error,
                "failed_at": datetime.utcnow().isoformat()
            }
            dlq_id = self.redis_client.xadd(self.dlq_stream, dlq_data)
            logger.error(f"✗ Event moved to DLQ: {msg_id} → {dlq_id}. Error: {error}")
            
            # Acknowledge original message
            self.redis_client.xack(stream_key, consumer_group, msg_id)
    
    def get_dlq_messages(self, count: int = 100) -> List[Dict[str, Any]]:
        """Retrieve messages from Dead Letter Queue"""
        messages = self.redis_client.xrange(self.dlq_stream, count=count)
        return [{"id": msg_id, **msg_data} for msg_id, msg_data in messages]
    
    def reprocess_dlq_message(self, msg_id: str, stream_key: str):
        """Attempt to reprocess a message from DLQ"""
        msg_data = self.redis_client.xrange(self.dlq_stream, msg_id, msg_id)
        if msg_data:
            _, data = msg_data[0]
            data.pop("error", None)
            data.pop("failed_at", None)
            data.pop("original_id", None)
            data["retries"] = "0"
            
            new_id = self.redis_client.xadd(stream_key, data)
            self.redis_client.xdel(self.dlq_stream, msg_id)
            logger.info(f"✓ DLQ message reprocessed: {msg_id} → {new_id}")
            return new_id
        return None
    
    def clear_dlq(self):
        """Clear all messages from DLQ"""
        self.redis_client.delete(self.dlq_stream)
        logger.info("✓ DLQ cleared")
    
    def get_stream_info(self, event_type: EventType) -> Dict[str, Any]:
        """Get stream statistics"""
        stream_key = f"events:{event_type.value}"
        info = self.redis_client.xinfo_stream(stream_key)
        return info


# Singleton instance for easy access
_event_bus_instance = None

def get_event_bus(redis_url: str = None) -> EventBus:
    """Get or create the event bus instance"""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(redis_url)
    return _event_bus_instance
