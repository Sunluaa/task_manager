from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE_URL = "http://auth-service:8001"
TASKS_SERVICE_URL = "http://tasks-service:8002"
NOTIFICATIONS_SERVICE_URL = "http://notifications-service:8003"

async def forward_request(service_url: str, path: str, method: str, headers: dict, body: Optional[bytes] = None, query_string: str = ""):
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{service_url}{path}"
        if query_string:
            url = f"{url}?{query_string}"
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            return response.status_code, response.headers, response.content
        except Exception as e:
            logger.error(f"Error forwarding request to {url}: {str(e)}")
            return 503, {}, b"Service unavailable"

@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def auth_gateway(request: Request, path: str):
    body = await request.body() if request.method != "GET" else None
    query_string = str(request.url.query) if request.url.query else ""
    status_code, headers, content = await forward_request(
        AUTH_SERVICE_URL,
        f"/auth/{path}",
        request.method,
        dict(request.headers),
        body,
        query_string
    )
    return {
        "status_code": status_code,
        "content": content,
        "headers": dict(headers)
    }

@app.api_route("/api/tasks/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def tasks_gateway(request: Request, path: str):
    body = await request.body() if request.method != "GET" else None
    query_string = str(request.url.query) if request.url.query else ""
    status_code, headers, content = await forward_request(
        TASKS_SERVICE_URL,
        f"/tasks/{path}",
        request.method,
        dict(request.headers),
        body,
        query_string
    )
    return {
        "status_code": status_code,
        "content": content,
        "headers": dict(headers)
    }

@app.api_route("/api/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def notifications_gateway(request: Request, path: str):
    body = await request.body() if request.method != "GET" else None
    query_string = str(request.url.query) if request.url.query else ""
    status_code, headers, content = await forward_request(
        NOTIFICATIONS_SERVICE_URL,
        f"/notifications/{path}",
        request.method,
        dict(request.headers),
        body,
        query_string
    )
    return {
        "status_code": status_code,
        "content": content,
        "headers": dict(headers)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
