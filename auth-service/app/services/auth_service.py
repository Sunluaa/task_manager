from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, TokenPayload
import os
import logging
import sys

# Add parent directory to path for importing shared_events
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from shared_events import Event, EventType, get_event_bus

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            role: str = payload.get("role")
            if email is None:
                return None
            return TokenPayload(sub=email, exp=payload.get("exp"), role=role)
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """Authenticate user. Returns (user, error_message) tuple."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None, None
        if not AuthService.verify_password(password, user.password_hash):
            return None, None
        if not user.is_active:
            return None, "Account is inactive. Please contact administrator"
        return user, None

    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> User:
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        hashed_password = AuthService.hash_password(user_create.password)
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            full_name=user_create.full_name,
            role=user_create.role.value if hasattr(user_create.role, 'value') else str(user_create.role),
            is_active=1 if user_create.is_active else 0
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Publish USER_CREATED event
        try:
            event_bus = get_event_bus()
            event = Event(
                event_type=EventType.USER_CREATED,
                aggregate_id=str(db_user.id),
                aggregate_type="user",
                data={
                    "email": db_user.email,
                    "full_name": db_user.full_name,
                    "role": db_user.role,
                    "user_id": db_user.id
                }
            )
            event_bus.publish(event)
            logger.info(f"✓ USER_CREATED event published for user: {db_user.email}")
        except Exception as e:
            logger.error(f"✗ Failed to publish USER_CREATED event: {e}")
        
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, email: Optional[str] = None, 
                   full_name: Optional[str] = None, role: Optional[UserRole] = None) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if email:
            user.email = email
        if full_name:
            user.full_name = full_name
        if role:
            user.role = role
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def toggle_user_active(db: Session, user_id: int) -> Optional[User]:
        """Toggle user active status (activate/deactivate)."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.is_active = 1 - user.is_active  # Toggle between 0 and 1
        db.commit()
        db.refresh(user)
        logger.info(f"User {user.email} active status changed to {bool(user.is_active)}")
        return user

    @staticmethod
    def set_user_active(db: Session, user_id: int, is_active: bool) -> Optional[User]:
        """Set user active status explicitly."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.is_active = 1 if is_active else 0
        db.commit()
        db.refresh(user)
        logger.info(f"User {user.email} active status set to {is_active}")
        return user
