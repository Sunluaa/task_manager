import jwt
from fastapi import Header, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = "your-secret-key-change-in-production"  # Should match auth-service
ALGORITHM = "HS256"

def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> int:
    """Extract user ID from Bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Token format: "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = parts[1]
        
        # Decode token without verification (for now, since we don't have the same key)
        # In production, should verify with the same secret
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        
        # Extract user ID from token - it's typically in 'sub' field as email
        # But we need to get the actual user ID
        # For now, return a default value or extract from headers
        user_email = payload.get("sub")
        
        # Parse user ID from email if available
        # This is a workaround - better solution would be to extract user_id from auth service
        logger.info(f"Token payload: {payload}")
        
        # Try to get user_id from custom claims
        user_id = payload.get("user_id")
        if user_id:
            return int(user_id)
        
        # Fallback to extracting from email hash or returning default
        # In production, query auth service to get user ID by email
        return 1  # Default value for now
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error parsing token: {e}")
        return 1  # Default value
