from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    token = authorization.split(" ")[1]
    token_payload = AuthService.verify_token(token)
    if not token_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = AuthService.get_user_by_email(db, token_payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = AuthService.register_user(db, user)
        logger.info(f"User registered: {db_user.email}")
        return db_user
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/users", response_model=UserResponse)
async def create_user_admin(user: UserCreate, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        db_user = AuthService.register_user(db, user)
        logger.info(f"User created by admin: {db_user.email}")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"User creation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user, error_message = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        if error_message:
            logger.warning(f"Login blocked - account inactive: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message
            )
        else:
            logger.warning(f"Failed login attempt: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/verify", response_model=UserResponse)
async def verify_token(current_user = Depends(get_current_user)):
    return current_user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = AuthService.get_all_users(db, skip, limit)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    user = AuthService.update_user(
        db, user_id,
        email=user_update.email,
        full_name=user_update.full_name,
        role=user_update.role
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User updated: {user.email}")
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    if not AuthService.delete_user(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User deleted: {user_id}")
    return {"detail": "User deleted"}

@router.get("/user-by-email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(user_id: int, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    """Toggle user active/inactive status (admin only)"""
    user = AuthService.toggle_user_active(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User {user.email} active status toggled by admin to: {bool(user.is_active)}")
    return user

@router.put("/users/{user_id}/set-active", response_model=UserResponse)
async def set_user_active(user_id: int, is_active: bool, admin_user = Depends(require_admin), db: Session = Depends(get_db)):
    """Set user active status explicitly (admin only)"""
    user = AuthService.set_user_active(db, user_id, is_active)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User {user.email} active status set to {is_active} by admin")
    return user
