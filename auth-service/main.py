from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.db.database import init_db
from app.controllers.auth_controller import router as auth_router
from app.services.auth_service import AuthService
from app.db.database import SessionLocal
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service", version="1.0.0")

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
    
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@admin.admin").first()
        if not admin_user:
            user = User(
                email="admin@admin.admin",
                password_hash=AuthService.hash_password("admin"),
                full_name="Admin",
                role=UserRole.ADMIN,
                is_active=1
            )
            db.add(user)
            db.commit()
            logger.info("Default admin user created")
    finally:
        db.close()

app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
