import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.redis_client import RedisClient
import redis.asyncio as redis

logger = logging.getLogger(__name__)

QUEUE_NAME = "queues:notifications"
DLQ_NAME = "dlq:notifications"
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes in seconds


class NotificationQueue:
    @staticmethod
    async def enqueue_notification(payload: Dict[str, Any]) -> str:
        """
        Add notification to queue
        payload: {user_id, title, message, ...}
        Returns: task_id
        """
        try:
            client = await RedisClient.get_client()
            task_id = f"{datetime.utcnow().isoformat()}"
            
            task_data = {
                "task_id": task_id,
                "payload": payload,
                "retries": 0,
                "created_at": datetime.utcnow().isoformat(),
                "attempts": [],
            }
            
            # Use Redis List (LPUSH) for queue
            await client.lpush(QUEUE_NAME, json.dumps(task_data))
            logger.info(f"Notification enqueued: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Failed to enqueue notification: {e}")
            raise

    @staticmethod
    async def dequeue_notification() -> Optional[Dict[str, Any]]:
        """
        Get next notification from queue (blocking right pop)
        Returns: task_data or None
        """
        try:
            client = await RedisClient.get_client()
            # BRPOP blocks until item available (timeout=1 to avoid infinite block)
            result = await client.brpop(QUEUE_NAME, timeout=1)
            
            if result:
                _, task_json = result
                task_data = json.loads(task_json)
                logger.info(f"Notification dequeued: {task_data['task_id']}")
                return task_data
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue notification: {e}")
            return None

    @staticmethod
    async def mark_as_retry(task_data: Dict[str, Any]) -> bool:
        """
        Requeue failed task with incremented retry count
        Moves to DLQ if max retries exceeded
        Returns: True if requeued, False if moved to DLQ
        """
        try:
            client = await RedisClient.get_client()
            task_id = task_data["task_id"]
            retries = task_data.get("retries", 0) + 1
            
            if retries >= MAX_RETRIES:
                # Move to Dead Letter Queue
                task_data["retries"] = retries
                task_data["failed_at"] = datetime.utcnow().isoformat()
                task_data["status"] = "failed"
                
                await client.lpush(DLQ_NAME, json.dumps(task_data))
                logger.warning(f"Task moved to DLQ after {retries} retries: {task_id}")
                return False
            else:
                # Requeue with increased retry count
                task_data["retries"] = retries
                task_data["attempts"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "retry_number": retries
                })
                
                await client.lpush(QUEUE_NAME, json.dumps(task_data))
                logger.info(f"Task requeued (attempt {retries}/{MAX_RETRIES}): {task_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to mark task as retry: {e}")
            return False

    @staticmethod
    async def mark_as_completed(task_data: Dict[str, Any]) -> bool:
        """Mark task as successfully completed"""
        try:
            client = await RedisClient.get_client()
            task_id = task_data["task_id"]
            completed_data = {
                **task_data,
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
            }
            
            # Store completed tasks for audit (with 24h TTL)
            completed_key = f"completed:{task_id}"
            await client.setex(
                completed_key,
                86400,  # 24 hours
                json.dumps(completed_data)
            )
            
            logger.info(f"Task marked as completed: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark task as completed: {e}")
            return False

    @staticmethod
    async def get_queue_stats() -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            client = await RedisClient.get_client()
            queue_len = await client.llen(QUEUE_NAME)
            dlq_len = await client.llen(DLQ_NAME)
            
            return {
                "queue_length": queue_len,
                "dlq_length": dlq_len,
                "queue_name": QUEUE_NAME,
                "dlq_name": DLQ_NAME,
            }
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_dlq_items(limit: int = 10) -> list:
        """Get items from Dead Letter Queue"""
        try:
            client = await RedisClient.get_client()
            items = await client.lrange(DLQ_NAME, 0, limit - 1)
            return [json.loads(item) for item in items]
        except Exception as e:
            logger.error(f"Failed to get DLQ items: {e}")
            return []

    @staticmethod
    async def clear_queue() -> bool:
        """Clear notification queue (for testing)"""
        try:
            client = await RedisClient.get_client()
            await client.delete(QUEUE_NAME)
            logger.warning("Notification queue cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return False
