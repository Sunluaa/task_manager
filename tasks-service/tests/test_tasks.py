import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Make sure we import from tasks-service
tasks_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if tasks_service_path not in sys.path:
    sys.path.insert(0, tasks_service_path)

from app.db.database import Base, get_db
from main import app as tasks_app
app = tasks_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"

def test_get_tasks():
    client.post(
        "/tasks",
        json={
            "title": "Task 1",
            "description": "Description 1",
            "priority": "medium"
        }
    )
    client.post(
        "/tasks",
        json={
            "title": "Task 2",
            "description": "Description 2",
            "priority": "low"
        }
    )
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_get_task_by_id():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Specific Task",
            "description": "Specific Description",
            "priority": "high"
        }
    )
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Task"
    assert data["id"] == task_id

def test_update_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Update Test",
            "description": "Original",
            "priority": "low"
        }
    )
    task_id = create_response.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated Description",
            "priority": "high"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"

def test_delete_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Delete Test",
            "description": "To Delete",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_task_validation():
    response = client.post(
        "/tasks",
        json={
            "title": "",
            "description": "Missing title",
            "priority": "high"
        }
    )
    assert response.status_code == 422

def test_add_worker_to_task():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Worker Task",
            "description": "Task for worker",
            "priority": "medium"
        }
    )
    task_id = create_response.json()["id"]
    response = client.post(f"/tasks/{task_id}/add-worker/2")
    assert response.status_code == 200

def test_complete_task_by_worker():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Complete Test",
            "description": "Worker completes",
            "priority": "high"
        }
    )
    task_id = create_response.json()["id"]
    # First assign the worker to the task
    client.post(f"/tasks/{task_id}/add-worker/2")
    # Now mark as completed
    response = client.post(f"/tasks/{task_id}/complete?user_id=2")
    assert response.status_code == 200

def test_filter_tasks_by_status():
    client.post(
        "/tasks",
        json={
            "title": "New Task",
            "description": "Status new",
            "priority": "medium"
        }
    )
    client.post(
        "/tasks",
        json={
            "title": "Completed Task",
            "description": "Status completed",
            "priority": "low"
        }
    )
    response = client.get("/tasks?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert all(task["status"] == "completed" for task in data)
