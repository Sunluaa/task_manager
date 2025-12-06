from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.db.database import init_db
from app.controllers.task_controller import router as task_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tasks Service", version="1.0.0")

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

app.include_router(task_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "tasks-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
