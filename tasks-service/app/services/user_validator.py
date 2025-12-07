"""
User validation service - communicates with auth-service
"""
import logging
import os
from typing import Optional, List

logger = logging.getLogger(__name__)

# Auth service endpoint
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

class UserValidator:
    @staticmethod
    def validate_active_users(worker_ids: List[int]) -> tuple[bool, Optional[str]]:
        """
        Validate that all worker IDs correspond to active users
        Returns: (is_valid, error_message)
        """
        if not worker_ids:
            return True, None
        
        try:
            import requests
            
            # Check each worker ID
            for worker_id in worker_ids:
                try:
                    response = requests.get(
                        f"{AUTH_SERVICE_URL}/auth/users/{worker_id}",
                        timeout=5
                    )
                    
                    if response.status_code == 404:
                        return False, f"Worker with ID {worker_id} not found"
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        if not user_data.get("is_active"):
                            return False, f"Worker {user_data.get('full_name', f'ID {worker_id}')} is inactive and cannot be assigned to tasks"
                    else:
                        logger.warning(f"Unexpected response from auth service for user {worker_id}: {response.status_code}")
                        # Don't fail on auth service errors, just log
                        
                except requests.RequestException as e:
                    logger.error(f"Error checking user {worker_id} status: {e}")
                    # Don't fail if auth service is unavailable
                    pass
            
            return True, None
            
        except ImportError:
            logger.warning("requests library not available for user validation")
            return True, None  # Allow if we can't validate
        except Exception as e:
            logger.error(f"Error validating users: {e}")
            return True, None  # Allow if validation fails

    @staticmethod
    async def validate_active_users_async(worker_ids: List[int]) -> tuple[bool, Optional[str]]:
        """
        Async version of validate_active_users
        """
        # For now, use sync version
        # In production, could use httpx for async HTTP
        return UserValidator.validate_active_users(worker_ids)
